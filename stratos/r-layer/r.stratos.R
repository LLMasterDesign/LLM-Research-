#!/usr/bin/env Rscript
# ▛//▞▞ ⟦⎊⟧ :: R.STRATOS :: ANALYSIS.LAYER ⫸
#
# R-based layer for:
# - Document generation with tables
# - Statistical analysis
# - Report printing with v8sl spec reintegration
# - Data validation and quality checks

library(jsonlite)

# Ritual validation in R
validate_ritual <- function(ritual, secret) {
  if (is.null(ritual$auth_key)) {
    return(TRUE)  # Unsigned ritual
  }
  
  payload <- paste0(ritual$ask, ritual$boot, ritual$seal, secret)
  computed <- digest::digest(payload, algo = "sha256", serialize = FALSE)
  
  computed == ritual$auth_key
}

# Load op spec from TOML (via JSON intermediate)
load_spec <- function(path) {
  # Assume spec was converted to JSON by engine or cloud layer
  json_path <- sub("\\.toml$", ".json", path)
  
  if (file.exists(json_path)) {
    fromJSON(json_path, simplifyVector = FALSE)
  } else {
    stop("Spec JSON not found. Convert TOML to JSON first.")
  }
}

# Generate markdown report with ritual markers
generate_report <- function(spec, outputs, output_path = "report.md") {
  lines <- c(
    spec$ritual$ask,
    spec$ritual$boot,
    "",
    paste0("# ", spec$meta$name),
    paste0("**Version:** ", spec$meta$version),
    paste0("**Operator:** ", spec$meta$operator),
    "",
    "## Execution Results",
    ""
  )
  
  # Add results for each step
  for (i in seq_along(spec$plan)) {
    step <- spec$plan[[i]]
    lines <- c(
      lines,
      paste0("### Step ", i, ": ", step$id),
      paste0("**Type:** `", step$type, "`"),
      ""
    )
    
    # Add output if available
    if (!is.null(outputs[[step$id]])) {
      lines <- c(
        lines,
        "**Output:**",
        "```",
        outputs[[step$id]],
        "```",
        ""
      )
    }
  }
  
  # Add seal
  lines <- c(lines, "", spec$ritual$seal)
  
  # Write report
  writeLines(lines, output_path)
  message("✓ Report generated: ", output_path)
  
  output_path
}

# Generate data summary table
summarize_data <- function(data, title = "Data Summary") {
  summary_df <- data.frame(
    Variable = names(data),
    Type = sapply(data, class),
    Count = sapply(data, length),
    NAs = sapply(data, function(x) sum(is.na(x))),
    stringsAsFactors = FALSE
  )
  
  list(
    title = title,
    summary = summary_df
  )
}

# Print table in ritual format
print_ritual_table <- function(df, title = NULL) {
  if (!is.null(title)) {
    cat("▛//▞▞ ⟦⎊⟧ ::", toupper(title), "⫸\n\n")
  }
  
  print(knitr::kable(df, format = "markdown"))
  
  cat("\n::∎\n")
}

# Validate v8sl spec structure
validate_v8sl_spec <- function(spec) {
  required <- c("ritual", "meta", "kernel", "plan")
  missing <- setdiff(required, names(spec))
  
  if (length(missing) > 0) {
    stop("Missing required sections: ", paste(missing, collapse = ", "))
  }
  
  # Validate ritual
  if (is.null(spec$ritual$ask) || is.null(spec$ritual$boot) || is.null(spec$ritual$seal)) {
    stop("Ritual must contain ask, boot, and seal")
  }
  
  # Validate meta
  if (is.null(spec$meta$name) || is.null(spec$meta$version)) {
    stop("Meta must contain name and version")
  }
  
  TRUE
}

# Export spec to validated JSON
export_validated_spec <- function(spec, output_path) {
  # Validate first
  validate_v8sl_spec(spec)
  
  # Add validation metadata
  spec$validated <- list(
    timestamp = Sys.time(),
    validator = "r.stratos",
    version = "1.0.0"
  )
  
  # Write JSON
  write_json(spec, output_path, pretty = TRUE, auto_unbox = TRUE)
  
  message("✓ Validated spec exported: ", output_path)
  output_path
}

# CLI interface
main <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  
  if (length(args) == 0) {
    cat("Usage: r.stratos.R [command] [args...]\n")
    cat("Commands:\n")
    cat("  validate <spec.json>         - Validate v8sl spec\n")
    cat("  report <spec.json> <out.md>  - Generate markdown report\n")
    cat("  export <spec.json> <out.json> - Export validated spec\n")
    quit(status = 1)
  }
  
  command <- args[1]
  
  if (command == "validate") {
    spec_path <- args[2]
    spec <- load_spec(spec_path)
    validate_v8sl_spec(spec)
    cat("✓ Spec is valid\n")
    
  } else if (command == "report") {
    spec_path <- args[2]
    output_path <- args[3]
    spec <- load_spec(spec_path)
    # Load outputs if available
    outputs_path <- "work/outputs.json"
    outputs <- if (file.exists(outputs_path)) {
      fromJSON(outputs_path, simplifyVector = FALSE)
    } else {
      list()
    }
    generate_report(spec, outputs, output_path)
    
  } else if (command == "export") {
    spec_path <- args[2]
    output_path <- args[3]
    spec <- load_spec(spec_path)
    export_validated_spec(spec, output_path)
    
  } else {
    cat("Unknown command:", command, "\n")
    quit(status = 1)
  }
}

# Run if called directly
if (!interactive()) {
  main()
}
