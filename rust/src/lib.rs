//! ///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂

pub const BANNER: &str = "///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂";

use regex::Regex;

pub struct Tokens {
    imprint: Regex,
    colon2: Regex,
    open_minor: Regex,
    section_head: Regex,
    section_tail: Regex,
    named_section: Regex,
}

impl Tokens {
    pub fn new() -> Self {
        Self {
            imprint: Regex::new(r"//▞▞").unwrap(),
            colon2: Regex::new(r"▞▞").unwrap(),
            open_minor: Regex::new(r"//▞").unwrap(),
            section_head: Regex::new(r"▛///▞").unwrap(),
            section_tail: Regex::new(r"▞▞//▟").unwrap(),
            named_section: Regex::new(r"▛▞\s+(.+?)\s+▞//").unwrap(),
        }
    }

    pub fn classify(&self, s: &str) -> &'static str {
        // Order matters: check more specific patterns first
        if self.imprint.is_match(s) {
            "IMPRINT"
        } else if self.section_head.is_match(s) {
            "SECTION_HEAD"
        } else if self.section_tail.is_match(s) {
            "SECTION_TAIL"
        } else if self.named_section.is_match(s) {
            "NAMED_SECTION"
        } else if self.colon2.is_match(s) {
            "COLON2"
        } else if self.open_minor.is_match(s) {
            "OPEN_MINOR"
        } else {
            "TEXT"
        }
    }

    pub fn extract_section_name(&self, s: &str) -> Option<String> {
        self.named_section
            .captures(s)
            .and_then(|cap| cap.get(1))
            .map(|m| m.as_str().to_string())
    }
}

impl Default for Tokens {
    fn default() -> Self {
        Self::new()
    }
}

pub fn lawline() {
    println!("{}", BANNER);
}
