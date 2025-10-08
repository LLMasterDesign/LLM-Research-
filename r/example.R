# ///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
source("boot.R")

lawline()

# ▛▞ Token Classification Demo ▞//
cat("Demonstrating token classification:\n")
# ▞▞//▟

examples <- c(
  "//▞▞ This is an imprint",
  "SECTION_HEAD marker: Section begins",
  "SECTION_TAIL marker: Section ends",
  "NAMED_SECTION marker: StatModel",
  "▞▞ Double colon semantics",
  "//▞ Minor open",
  "Regular text line"
)

# ▛▞ Classification Loop ▞//
for (ex in examples) {
  token_type <- classify(ex)
  cat(sprintf("%-40s -> %s\n", ex, token_type))
  
  if (token_type == "NAMED_SECTION") {
    name <- extract_section_name(ex)
    cat(sprintf("  └─ Section name: %s\n", name))
  }
}
# ▞▞//▟

# ▛▞ R Syntax Features ▞//
cat("\nR Syntax Features:\n")
cat("- Vectorized operations by default\n")
cat("- Formula notation for models\n")
cat("- Data frame as primary structure\n")
# ▞▞//▟

# ▛▞ Statistical Computing Example ▞//
data <- data.frame(
  x = 1:10,
  y = rnorm(10)
)
cat("\nGenerated sample data with", nrow(data), "observations\n")
# ▞▞//▟
