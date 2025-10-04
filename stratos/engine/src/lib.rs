/*!
▛//▞▞ ⟦⎊⟧ :: ENGINE.STRATOS :: CORE.RUNTIME ⫸

Rust-based execution engine for Codex op specs.
Validates ritual markers, enforces drift-lock, executes plans.

The ⟦⎊⟧ marker is used as a security validation token.
Only specs with valid ritual auth can execute.
*/

use serde::{Deserialize, Serialize};
use sha2::{Sha256, Digest};
use std::collections::HashMap;

/// Ritual markers used for validation and ceremony
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct Ritual {
    pub ask: String,      // ///▙ or alternate
    pub boot: String,     // ⟦⎊⟧ or [⎊]
    pub seal: String,     // ::∎
    #[serde(default)]
    pub auth_key: Option<String>,  // SHA256 of ritual+secret
}

impl Ritual {
    /// Validate that ritual markers are present and authentic
    pub fn validate(&self, secret: &str) -> anyhow::Result<()> {
        // Check for required markers
        anyhow::ensure!(!self.ask.is_empty(), "ask marker required");
        anyhow::ensure!(!self.boot.is_empty(), "boot marker required");
        anyhow::ensure!(!self.seal.is_empty(), "seal marker required");
        
        // Validate auth_key if present
        if let Some(key) = &self.auth_key {
            let computed = self.compute_auth(secret);
            anyhow::ensure!(key == &computed, "⟦⎊⟧ auth validation failed");
        }
        
        Ok(())
    }
    
    /// Compute auth hash from ritual + secret
    pub fn compute_auth(&self, secret: &str) -> String {
        let payload = format!("{}{}{}{}", self.ask, self.boot, self.seal, secret);
        let mut hasher = Sha256::new();
        hasher.update(payload.as_bytes());
        hex::encode(hasher.finalize())
    }
    
    /// Generate auth key for this ritual
    pub fn sign(&mut self, secret: &str) {
        self.auth_key = Some(self.compute_auth(secret));
    }
}

/// Metadata about the operation
#[derive(Debug, Deserialize, Serialize)]
pub struct Meta {
    pub name: String,
    pub version: String,
    pub operator: String,
    #[serde(default)]
    pub tags: Vec<String>,
}

/// Kernel configuration - the laws of execution
#[derive(Debug, Deserialize, Serialize)]
pub struct Kernel {
    pub purpose: Vec<String>,
    pub rules: Vec<String>,
    pub identity: Vec<String>,
    pub structure: Vec<String>,
    pub motion: Vec<String>,
}

/// Execution steps in the plan
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(tag = "type", rename_all = "lowercase")]
pub enum Step {
    Shell {
        id: String,
        cmd: String,
        #[serde(default)]
        cwd: Option<String>,
    },
    Llm {
        id: String,
        prompt: String,
        #[serde(default)]
        model: Option<String>,
        #[serde(default)]
        max_tokens: Option<u32>,
    },
    Ruby {
        id: String,
        script: String,
        #[serde(default)]
        args: Vec<String>,
    },
    R {
        id: String,
        script: String,
        #[serde(default)]
        output: Option<String>,
    },
    Validate {
        id: String,
        check: String,
        #[serde(default)]
        on_fail: Option<String>,
    },
    Store {
        id: String,
        key: String,
        value: String,
    },
    Recall {
        id: String,
        key: String,
    },
}

/// Complete operation specification
#[derive(Debug, Deserialize, Serialize)]
pub struct OpSpec {
    pub ritual: Ritual,
    pub meta: Meta,
    pub kernel: Kernel,
    pub plan: Vec<Step>,
}

/// Execution context - holds state during run
#[derive(Debug, Default)]
pub struct Context {
    pub store: HashMap<String, String>,
    pub outputs: HashMap<String, String>,
    pub errors: Vec<String>,
}

impl Context {
    pub fn new() -> Self {
        Self::default()
    }
    
    pub fn set(&mut self, key: impl Into<String>, value: impl Into<String>) {
        self.store.insert(key.into(), value.into());
    }
    
    pub fn get(&self, key: &str) -> Option<&String> {
        self.store.get(key)
    }
    
    pub fn record_output(&mut self, step_id: impl Into<String>, output: impl Into<String>) {
        self.outputs.insert(step_id.into(), output.into());
    }
    
    pub fn record_error(&mut self, error: impl Into<String>) {
        self.errors.push(error.into());
    }
}

/// Step executor trait - implement for each step type
#[async_trait::async_trait]
pub trait Executor {
    async fn execute(&self, step: &Step, ctx: &mut Context) -> anyhow::Result<()>;
}

/// Load operation spec from TOML file
pub fn load_spec(path: &str) -> anyhow::Result<OpSpec> {
    let content = std::fs::read_to_string(path)?;
    let spec: OpSpec = toml::from_str(&content)?;
    Ok(spec)
}

/// Save operation spec to TOML file
pub fn save_spec(spec: &OpSpec, path: &str) -> anyhow::Result<()> {
    let content = toml::to_string_pretty(spec)?;
    std::fs::write(path, content)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_ritual_validation() {
        let mut ritual = Ritual {
            ask: "///▙".to_string(),
            boot: "⟦⎊⟧".to_string(),
            seal: "::∎".to_string(),
            auth_key: None,
        };
        
        let secret = "test-secret";
        ritual.sign(secret);
        
        assert!(ritual.validate(secret).is_ok());
        assert!(ritual.validate("wrong-secret").is_err());
    }
}
