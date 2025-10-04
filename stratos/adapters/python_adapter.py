#!/usr/bin/env python3
"""
▛//▞▞ ⟦⎊⟧ :: PYTHON.ADAPTER :: STRATOS.BRIDGE ⫸

Python adapter for calling stratos layers from Telegram bot
and other Python contexts.

Bridges:
- Telegram bot → engine.stratos (Rust)
- Python → cloud.stratos (Ruby)
- Python → r.stratos (R)
"""

import json
import subprocess
import hashlib
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class Ritual:
    """Ritual markers for validation"""
    ask: str = "///▙"
    boot: str = "⟦⎊⟧"
    seal: str = "::∎"
    auth_key: Optional[str] = None
    
    def compute_auth(self, secret: str) -> str:
        """Compute auth hash (matches Rust/Ruby implementation)"""
        payload = f"{self.ask}{self.boot}{self.seal}{secret}"
        return hashlib.sha256(payload.encode()).hexdigest()
    
    def sign(self, secret: str):
        """Sign this ritual with secret"""
        self.auth_key = self.compute_auth(secret)
    
    def validate(self, secret: str) -> bool:
        """Validate auth"""
        if self.auth_key is None:
            return True  # Unsigned rituals allowed
        return self.auth_key == self.compute_auth(secret)


@dataclass
class OpSpec:
    """Operation specification"""
    ritual: Ritual
    meta: Dict[str, Any]
    kernel: Dict[str, List[str]]
    plan: List[Dict[str, Any]]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "ritual": asdict(self.ritual),
            "meta": self.meta,
            "kernel": self.kernel,
            "plan": self.plan
        }
    
    def to_toml(self) -> str:
        """Convert to TOML format"""
        try:
            import toml
            return toml.dumps(self.to_dict())
        except ImportError:
            raise ImportError("toml package required. Install: pip install toml")
    
    def save(self, path: str):
        """Save spec to TOML file"""
        with open(path, 'w') as f:
            f.write(self.to_toml())


class StratosEngine:
    """Interface to engine.stratos (Rust runtime)"""
    
    def __init__(self, engine_path: Optional[str] = None, secret: Optional[str] = None):
        self.engine_path = engine_path or self._find_engine()
        self.secret = secret or os.getenv('CODEX_SECRET', 'default-secret')
    
    def _find_engine(self) -> str:
        """Locate engine.stratos binary"""
        possible_paths = [
            'stratos/engine/target/release/stratos',
            '../stratos/engine/target/release/stratos',
            '/usr/local/bin/stratos',
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        return 'stratos'  # Hope it's in PATH
    
    def execute(self, spec_path: str) -> tuple[bool, str]:
        """Execute an op spec"""
        env = os.environ.copy()
        env['CODEX_SECRET'] = self.secret
        
        try:
            result = subprocess.run(
                [self.engine_path, spec_path],
                capture_output=True,
                text=True,
                env=env,
                timeout=300
            )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            return success, output
        
        except subprocess.TimeoutExpired:
            return False, "Execution timeout (300s)"
        except Exception as e:
            return False, f"Execution error: {e}"


class CloudStratos:
    """Interface to cloud.stratos (Ruby orchestration)"""
    
    def __init__(self, script_path: Optional[str] = None):
        self.script_path = script_path or self._find_script()
    
    def _find_script(self) -> str:
        """Locate cloud.stratos.rb"""
        possible_paths = [
            'stratos/cloud/cloud.stratos.rb',
            '../stratos/cloud/cloud.stratos.rb',
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        return 'cloud.stratos.rb'
    
    def execute_spec(self, spec_path: str) -> tuple[bool, str]:
        """Execute a spec via cloud layer"""
        try:
            result = subprocess.run(
                ['ruby', self.script_path, 'execute', '-s', spec_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            return success, output
        
        except Exception as e:
            return False, f"Cloud execution error: {e}"
    
    def store_memory(self, key: str, value: Any) -> bool:
        """Store value in cloud memory"""
        value_json = json.dumps(value) if not isinstance(value, str) else value
        
        try:
            result = subprocess.run(
                ['ruby', self.script_path, 'store', '-k', key, '-v', value_json],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def recall_memory(self, key: str) -> Optional[Any]:
        """Recall value from cloud memory"""
        try:
            result = subprocess.run(
                ['ruby', self.script_path, 'recall', '-k', key],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return result.stdout.strip()
            
            return None
        except Exception:
            return None


class RStratos:
    """Interface to r.stratos (R analysis layer)"""
    
    def __init__(self, script_path: Optional[str] = None):
        self.script_path = script_path or self._find_script()
    
    def _find_script(self) -> str:
        """Locate r.stratos.R"""
        possible_paths = [
            'stratos/r-layer/r.stratos.R',
            '../stratos/r-layer/r.stratos.R',
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        return 'r.stratos.R'
    
    def validate_spec(self, spec_path: str) -> tuple[bool, str]:
        """Validate a spec using R layer"""
        try:
            result = subprocess.run(
                ['Rscript', self.script_path, 'validate', spec_path],
                capture_output=True,
                text=True
            )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            return success, output
        except Exception as e:
            return False, f"R validation error: {e}"
    
    def generate_report(self, spec_path: str, output_path: str) -> tuple[bool, str]:
        """Generate markdown report"""
        try:
            result = subprocess.run(
                ['Rscript', self.script_path, 'report', spec_path, output_path],
                capture_output=True,
                text=True
            )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            return success, output
        except Exception as e:
            return False, f"R report error: {e}"


# Convenience function for quick execution
def execute_op(spec_path: str, secret: Optional[str] = None) -> tuple[bool, str]:
    """Execute an operation spec"""
    engine = StratosEngine(secret=secret)
    return engine.execute(spec_path)


# Example usage
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python_adapter.py <spec.toml>")
        sys.exit(1)
    
    spec_path = sys.argv[1]
    success, output = execute_op(spec_path)
    
    print(output)
    sys.exit(0 if success else 1)
