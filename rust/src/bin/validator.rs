// ///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
use lawline::Tokens;
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};
use walkdir::WalkDir;

#[derive(Debug, Serialize, Deserialize)]
struct TokenManifest {
    version: String,
    description: String,
    tokens: serde_json::Value,
    rules: Rules,
}

#[derive(Debug, Serialize, Deserialize)]
struct Rules {
    alignment: Vec<String>,
    validation: Vec<String>,
}

#[derive(Debug)]
struct ValidationError {
    file: PathBuf,
    line_num: usize,
    message: String,
}

struct Validator {
    tokens: Tokens,
    manifest: TokenManifest,
}

impl Validator {
    fn new(manifest_path: &Path) -> Result<Self, Box<dyn std::error::Error>> {
        let manifest_content = fs::read_to_string(manifest_path)?;
        let manifest: TokenManifest = serde_json::from_str(&manifest_content)?;
        Ok(Self {
            tokens: Tokens::new(),
            manifest,
        })
    }

    fn validate_file(&self, path: &Path) -> Vec<ValidationError> {
        let mut errors = Vec::new();

        let content = match fs::read_to_string(path) {
            Ok(c) => c,
            Err(e) => {
                errors.push(ValidationError {
                    file: path.to_path_buf(),
                    line_num: 0,
                    message: format!("Failed to read file: {}", e),
                });
                return errors;
            }
        };

        let lines: Vec<&str> = content.lines().collect();

        // Rule 1: Banner must appear in first 3 lines
        let has_banner = lines
            .iter()
            .take(3)
            .any(|line| line.contains("///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂"));

        if !has_banner {
            errors.push(ValidationError {
                file: path.to_path_buf(),
                line_num: 1,
                message: "Banner must appear in first 3 lines".to_string(),
            });
        }

        // Rule 2: Check section pairing
        let mut section_stack: Vec<(usize, String)> = Vec::new();

        for (i, line) in lines.iter().enumerate() {
            let line_num = i + 1;
            let classification = self.tokens.classify(line);

            match classification {
                "SECTION_HEAD" | "NAMED_SECTION" => {
                    section_stack.push((line_num, classification.to_string()));
                }
                "SECTION_TAIL" => {
                    if section_stack.is_empty() {
                        errors.push(ValidationError {
                            file: path.to_path_buf(),
                            line_num,
                            message: "Section tail without matching head".to_string(),
                        });
                    } else {
                        section_stack.pop();
                    }
                }
                _ => {}
            }
        }

        // Check for unclosed sections
        for (line_num, section_type) in section_stack {
            errors.push(ValidationError {
                file: path.to_path_buf(),
                line_num,
                message: format!("Unclosed section: {}", section_type),
            });
        }

        errors
    }

    fn validate_directory(&self, dir: &Path, extensions: &[&str]) -> Vec<ValidationError> {
        let mut all_errors = Vec::new();

        for entry in WalkDir::new(dir)
            .follow_links(true)
            .into_iter()
            .filter_map(|e| e.ok())
        {
            let path = entry.path();
            if path.is_file() {
                if let Some(ext) = path.extension() {
                    if extensions.contains(&ext.to_str().unwrap_or("")) {
                        let errors = self.validate_file(path);
                        all_errors.extend(errors);
                    }
                }
            }
        }

        all_errors
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂");
    println!("▛▞ Lawline Token Validator ▞//");
    println!("▞▞//▟\n");

    let manifest_path = Path::new("tokens.json");
    let validator = Validator::new(manifest_path)?;

    println!("Loaded manifest version: {}", validator.manifest.version);
    println!("Description: {}\n", validator.manifest.description);

    // Validate each language directory
    let validations = vec![
        ("Ruby", "ruby", vec!["rb"]),
        ("Rust", "rust/src", vec!["rs"]),
        ("R", "r", vec!["R"]),
    ];

    let mut total_errors = 0;

    for (lang, dir, exts) in validations {
        let path = Path::new(dir);
        if !path.exists() {
            println!("⚠ {} directory not found, skipping", lang);
            continue;
        }

        println!("▛///▞ Validating {} files", lang);
        let errors = validator.validate_directory(path, &exts);

        if errors.is_empty() {
            println!("✓ All {} files pass validation", lang);
        } else {
            println!("✗ Found {} error(s) in {} files:", errors.len(), lang);
            for error in &errors {
                println!(
                    "  {}:{} - {}",
                    error.file.display(),
                    error.line_num,
                    error.message
                );
            }
            total_errors += errors.len();
        }
        println!("▞▞//▟\n");
    }

    if total_errors == 0 {
        println!("✓ All validation checks passed!");
        Ok(())
    } else {
        println!("✗ Total errors: {}", total_errors);
        std::process::exit(1);
    }
}
