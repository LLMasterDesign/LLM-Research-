from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import imaplib
import email
from email.message import Message
from email import policy
import json
import os
import re


def _safe_int(raw: Optional[str], default: int) -> int:
    try:
        return int(raw) if raw is not None else default
    except Exception:
        return default


@dataclass
class EmailConfig:
    host: str
    username: str
    password: str
    port: int = 993
    mailbox: str = "INBOX"
    use_ssl: bool = True
    state_path: str = "data/imap_state.json"
    # Comma-separated keyword list, e.g. "invoice,appointment,delivery"
    keywords: str = ""
    # Max emails to fetch and summarize per request
    max_fetch: int = 20


class ImapState:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self._data: Dict[str, Any] = {}
        self._load()

    @property
    def last_uid(self) -> int:
        return _safe_int(self._data.get("last_uid"), 0)

    @last_uid.setter
    def last_uid(self, value: int) -> None:
        self._data["last_uid"] = int(value)
        self._save()

    def _load(self) -> None:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {}

    def _save(self) -> None:
        try:
            with open(self.path, "w") as f:
                json.dump(self._data, f)
        except Exception:
            pass


def _html_to_text(html: str) -> str:
    try:
        from bs4 import BeautifulSoup  # type: ignore

        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text(" ")
        text = re.sub(r"\s+", " ", text)
        return text.strip()
    except Exception:
        return re.sub(r"<[^>]+>", " ", html)


def _message_to_text(msg: Message) -> str:
    if msg.is_multipart():
        parts: List[str] = []
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type in ("text/plain", "text/html"):
                try:
                    payload = part.get_content()
                except Exception:
                    payload = part.get_payload(decode=True) or b""
                    try:
                        payload = payload.decode(errors="ignore")
                    except Exception:
                        payload = ""
                if not payload:
                    continue
                if content_type == "text/html":
                    parts.append(_html_to_text(str(payload)))
                else:
                    parts.append(str(payload))
        text = "\n".join(parts)
    else:
        try:
            payload = msg.get_content()
        except Exception:
            payload = msg.get_payload(decode=True) or b""
            try:
                payload = payload.decode(errors="ignore")
            except Exception:
                payload = ""
        content_type = msg.get_content_type()
        text = _html_to_text(str(payload)) if content_type == "text/html" else str(payload)
    text = re.sub(r"\r\n|\r", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_header_str(msg: Message, name: str) -> str:
    try:
        value = msg.get(name, "")
        if isinstance(value, str):
            return value
        return str(value)
    except Exception:
        return ""


def _score_relevance(subject: str, sender: str, text: str, keywords: List[str]) -> float:
    subject_l = subject.lower()
    text_l = text.lower()

    score = 0.0

    for kw in keywords:
        if kw and (kw in subject_l or kw in text_l):
            score += 8.0

    important_terms = [
        "invoice", "receipt", "payment", "paid", "due", "overdue",
        "order", "shipment", "delivery", "tracking", "schedule", "appointment",
        "verify", "confirm", "reset", "security", "code", "otp", "ticket",
        "failed", "declined", "refund", "credit", "debit",
    ]
    for term in important_terms:
        if term in subject_l or term in text_l:
            score += 2.0

    if re.search(r"[\$€£]\s?\d{1,3}(,\d{3})*(\.\d{2})?", text):
        score += 3.0

    promo_terms = ["unsubscribe", "newsletter", "sale", "deal", "promo", "marketing", "advert"]
    for term in promo_terms:
        if term in text_l:
            score -= 3.0

    if "noreply" in sender.lower() or "no-reply" in sender.lower():
        score -= 1.0

    if len(subject) >= 6:
        score += 0.5

    return score


def _extract_key_points(text: str) -> List[str]:
    points: List[str] = []

    amounts = re.findall(r"([\$€£]\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", text)
    if amounts:
        points.append(f"Amounts: {', '.join(amounts[:3])}")

    patterns = [
        (r"order\s*#?\s*([A-Za-z0-9-]{5,})", "Order"),
        (r"invoice\s*#?\s*([A-Za-z0-9-]{5,})", "Invoice"),
        (r"tracking\s*#?\s*([A-Za-z0-9-]{5,})", "Tracking"),
        (r"ticket\s*#?\s*([A-Za-z0-9-]{5,})", "Ticket"),
    ]
    for pat, label in patterns:
        ids = re.findall(pat, text, flags=re.I)
        if ids:
            points.append(f"{label}: {', '.join(ids[:3])}")

    actions = [
        (r"\b(confirm|verify|reset|approve|pay|schedule|reschedule|cancel)\b", "Action")
    ]
    for pat, label in actions:
        found = re.findall(pat, text, flags=re.I)
        if found:
            uniq = sorted({w.lower() for w in found})
            points.append(f"{label}: {', '.join(uniq[:5])}")

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if lines:
        gist = []
        for ln in lines:
            if len(ln) < 8:
                continue
            if "confidential" in ln.lower() and len(ln) > 140:
                continue
            gist.append(ln)
            if len(gist) >= 2:
                break
        if gist:
            points.append("Gist: " + " / ".join(gist))

    return points


def summarize_email(subject: str, sender: str, text: str) -> str:
    points = _extract_key_points(text)
    header = f"From: {sender}\nSubject: {subject}"
    if points:
        bullets = "\n".join(f"- {p}" for p in points)
        return f"{header}\n{bullets}"
    trimmed = (text[:200] + "...") if len(text) > 200 else text
    return f"{header}\n- {trimmed}"


@dataclass
class EmailItem:
    uid: int
    subject: str
    sender: str
    date: str
    text: str
    relevance: float


class EmailAgent:
    def __init__(self, config: EmailConfig):
        self.config = config
        self.state = ImapState(config.state_path)

    def _connect(self) -> imaplib.IMAP4:
        if self.config.use_ssl:
            client = imaplib.IMAP4_SSL(self.config.host, self.config.port)
        else:
            client = imaplib.IMAP4(self.config.host, self.config.port)
        client.login(self.config.username, self.config.password)
        status, _ = client.select(self.config.mailbox)
        if status != "OK":
            raise RuntimeError("Failed to select mailbox")
        return client

    def fetch_new(self, limit: Optional[int] = None) -> List[EmailItem]:
        limit = limit or self.config.max_fetch
        keywords = [kw.strip().lower() for kw in (self.config.keywords or "").split(",") if kw.strip()]

        client = self._connect()
        try:
            last_uid = self.state.last_uid
            if last_uid > 0:
                criteria = f"(UID {last_uid + 1}:*)"
            else:
                criteria = "(UNSEEN)"

            status, data = client.uid("SEARCH", None, criteria)
            if status != "OK":
                return []
            uid_bytes = (data[0] or b"").split()
            uids = [int(uid.decode()) for uid in uid_bytes][-limit:]
            items: List[EmailItem] = []

            for uid in uids:
                status, fetch_data = client.uid("FETCH", str(uid), "(RFC822)")
                if status != "OK" or not fetch_data or not isinstance(fetch_data[0], tuple):
                    continue
                raw = fetch_data[0][1]
                msg = email.message_from_bytes(raw, policy=policy.default)

                subject = _extract_header_str(msg, "Subject")
                sender = _extract_header_str(msg, "From")
                date = _extract_header_str(msg, "Date")
                text = _message_to_text(msg)

                relevance = _score_relevance(subject, sender, text, keywords)
                items.append(EmailItem(uid=uid, subject=subject, sender=sender, date=date, text=text, relevance=relevance))

            if uids:
                self.state.last_uid = max(uids)

            items.sort(key=lambda it: it.relevance, reverse=True)
            return items[:limit]
        finally:
            try:
                client.logout()
            except Exception:
                pass


def format_summaries_for_telegram(items: List[EmailItem], max_items: int = 8) -> str:
    if not items:
        return "No new relevant emails found."
    lines: List[str] = []
    for i, item in enumerate(items[:max_items], start=1):
        summary = summarize_email(item.subject, item.sender, item.text)
        summary = re.sub(r"\n{3,}", "\n\n", summary).strip()
        lines.append(f"[{i}] {summary}")
    return "\n\n".join(lines)
