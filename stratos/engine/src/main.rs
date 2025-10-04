/*!
▛//▞▞ ⟦⎊⟧ :: ENGINE.STRATOS :: MAIN.RUNTIME ⫸

Command-line interface for executing Codex operation specs.
*/

use engine_stratos::*;
use std::process::Command;
use std::env;

/// Execute shell command with proper shell invocation
fn run_shell(id: &str, cmd: &str, cwd: Option<&str>, ctx: &mut Context) -> anyhow::Result<()> {
    println!("⫸ run.shell [{}] :: {}", id, cmd);
    
    let mut command = if cfg!(target_os = "windows") {
        let mut c = Command::new("cmd");
        c.args(["/C", cmd]);
        c
    } else {
        let mut c = Command::new("sh");
        c.args(["-c", cmd]);
        c
    };
    
    if let Some(dir) = cwd {
        command.current_dir(dir);
    }
    
    let output = command.output()?;
    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);
    
    ctx.record_output(id, stdout.to_string());
    
    if !output.status.success() {
        ctx.record_error(format!("[{}] {}", id, stderr));
        anyhow::bail!("shell step [{}] failed: {}", id, stderr);
    }
    
    Ok(())
}

/// Execute LLM prompt (stub - integrate with your model)
fn run_llm(id: &str, prompt: &str, model: Option<&str>, ctx: &mut Context) -> anyhow::Result<()> {
    println!("⫸ run.llm [{}] :: model={:?}", id, model);
    println!("{}", prompt);
    
    // Save prompt for inspection
    let prompt_file = format!("work/{}.prompt.txt", id);
    std::fs::create_dir_all("work")?;
    std::fs::write(&prompt_file, prompt)?;
    
    // TODO: Call your LLM API here
    // For now, stub response
    let response = format!("LLM response for step: {}", id);
    ctx.record_output(id, response);
    
    Ok(())
}

/// Execute Ruby script via cloud.stratos
fn run_ruby(id: &str, script: &str, args: &[String], ctx: &mut Context) -> anyhow::Result<()> {
    println!("⫸ run.ruby [{}]", id);
    
    let script_file = format!("work/{}.rb", id);
    std::fs::write(&script_file, script)?;
    
    let mut cmd = Command::new("ruby");
    cmd.arg(&script_file);
    cmd.args(args);
    
    let output = cmd.output()?;
    let stdout = String::from_utf8_lossy(&output.stdout);
    
    ctx.record_output(id, stdout.to_string());
    
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        ctx.record_error(format!("[{}] {}", id, stderr));
        anyhow::bail!("ruby step [{}] failed", id);
    }
    
    Ok(())
}

/// Execute R script for analysis
fn run_r(id: &str, script: &str, output_path: Option<&str>, ctx: &mut Context) -> anyhow::Result<()> {
    println!("⫸ run.r [{}]", id);
    
    let script_file = format!("work/{}.R", id);
    std::fs::write(&script_file, script)?;
    
    let mut cmd = Command::new("Rscript");
    cmd.arg(&script_file);
    
    let output = cmd.output()?;
    let stdout = String::from_utf8_lossy(&output.stdout);
    
    if let Some(out_path) = output_path {
        std::fs::write(out_path, stdout.as_bytes())?;
    }
    
    ctx.record_output(id, stdout.to_string());
    
    Ok(())
}

/// Execute validation check
fn run_validate(id: &str, check: &str, on_fail: Option<&str>, ctx: &mut Context) -> anyhow::Result<()> {
    println!("⫸ validate [{}] :: {}", id, check);
    
    // Simple validation - check if key exists in context
    if check.starts_with("exists:") {
        let key = check.strip_prefix("exists:").unwrap();
        if ctx.get(key).is_none() {
            if let Some(msg) = on_fail {
                anyhow::bail!("validation failed [{}]: {}", id, msg);
            }
        }
    }
    
    Ok(())
}

/// Store value in context
fn run_store(id: &str, key: &str, value: &str, ctx: &mut Context) -> anyhow::Result<()> {
    println!("⫸ store [{}] :: {} = {}", id, key, value);
    ctx.set(key, value);
    Ok(())
}

/// Recall value from context
fn run_recall(id: &str, key: &str, ctx: &mut Context) -> anyhow::Result<()> {
    println!("⫸ recall [{}] :: {}", id, key);
    if let Some(value) = ctx.get(key) {
        println!("  → {}", value);
        ctx.record_output(id, value.clone());
    } else {
        ctx.record_error(format!("[{}] key not found: {}", id, key));
    }
    Ok(())
}

/// Execute a single step
fn execute_step(step: &Step, ctx: &mut Context) -> anyhow::Result<()> {
    match step {
        Step::Shell { id, cmd, cwd } => {
            run_shell(id, cmd, cwd.as_deref(), ctx)?;
        }
        Step::Llm { id, prompt, model, .. } => {
            run_llm(id, prompt, model.as_deref(), ctx)?;
        }
        Step::Ruby { id, script, args } => {
            run_ruby(id, script, args, ctx)?;
        }
        Step::R { id, script, output } => {
            run_r(id, script, output.as_deref(), ctx)?;
        }
        Step::Validate { id, check, on_fail } => {
            run_validate(id, check, on_fail.as_deref(), ctx)?;
        }
        Step::Store { id, key, value } => {
            run_store(id, key, value, ctx)?;
        }
        Step::Recall { id, key } => {
            run_recall(id, key, ctx)?;
        }
    }
    Ok(())
}

fn main() -> anyhow::Result<()> {
    // Parse arguments
    let args: Vec<String> = env::args().collect();
    let spec_path = args.get(1).map(|s| s.as_str()).unwrap_or("codex.op.toml");
    let secret = env::var("CODEX_SECRET").unwrap_or_else(|_| "default-secret".to_string());
    
    println!("▛//▞▞ ⟦⎊⟧ :: ENGINE.STRATOS :: LOADING ⫸");
    println!("  spec: {}", spec_path);
    
    // Load spec
    let spec = load_spec(spec_path)?;
    
    // Validate ritual
    println!("\n{}", spec.ritual.ask);
    println!("{}", spec.ritual.boot);
    println!("\n⫸ Validating ritual auth...");
    spec.ritual.validate(&secret)?;
    println!("  ✓ Ritual authenticated");
    
    // Show meta
    println!("\n⫸ Operation: {}", spec.meta.name);
    println!("  Version: {}", spec.meta.version);
    println!("  Operator: {}", spec.meta.operator);
    
    // Show kernel
    println!("\n⫸ Kernel:");
    println!("  Purpose: {:?}", spec.kernel.purpose);
    println!("  Rules: {:?}", spec.kernel.rules);
    
    // Execute plan
    println!("\n⫸ Executing plan ({} steps)...\n", spec.plan.len());
    
    let mut ctx = Context::new();
    for (idx, step) in spec.plan.iter().enumerate() {
        println!("[{}/{}]", idx + 1, spec.plan.len());
        if let Err(e) = execute_step(step, &mut ctx) {
            eprintln!("✗ Step failed: {}", e);
            ctx.record_error(format!("Step failed: {}", e));
            // Continue or break depending on your error handling policy
        }
        println!();
    }
    
    // Summary
    println!("\n⫸ Execution complete");
    println!("  Steps: {}", spec.plan.len());
    println!("  Outputs: {}", ctx.outputs.len());
    println!("  Errors: {}", ctx.errors.len());
    
    if !ctx.errors.is_empty() {
        println!("\n⚠ Errors:");
        for err in &ctx.errors {
            println!("  • {}", err);
        }
    }
    
    println!("\n{}", spec.ritual.seal);
    
    Ok(())
}
