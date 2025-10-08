# ///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
BANNER <- "///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂"
lawline <- function() cat(BANNER, "\n")

# Token classification system
classify <- function(s) {
  if (grepl("//▞▞", s)) return("IMPRINT")
  if (grepl("▛///▞", s)) return("SECTION_HEAD")
  if (grepl("▞▞//▟", s)) return("SECTION_TAIL")
  if (grepl("▛▞\\s+.+?\\s+▞//", s)) return("NAMED_SECTION")
  if (grepl("▞▞", s)) return("COLON2")
  if (grepl("//▞", s)) return("OPEN_MINOR")
  "TEXT"
}

extract_section_name <- function(s) {
  if (grepl("▛▞\\s+.+?\\s+▞//", s)) {
    sub(".*▛▞\\s+(.+?)\\s+▞//.*", "\\1", s)
  } else {
    NA
  }
}
