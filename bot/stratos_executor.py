"""
▛//▞▞ ⟦⎊⟧ :: STRATOS.EXECUTOR :: BOT.INTEGRATION ⫸

Integration layer between Telegram bot and stratos engine.
Allows users to execute operation specs from Telegram commands.
"""

import sys
import os
from pathlib import Path

# Add stratos adapters to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'stratos' / 'adapters'))

from python_adapter import (
    StratosEngine,
    CloudStratos,
    RStratos,
    OpSpec,
    Ritual
)

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class StratosExecutor:
    """Executes stratos ops from Telegram bot context"""
    
    def __init__(self, secret: Optional[str] = None):
        self.secret = secret or os.getenv('CODEX_SECRET', 'default-secret')
        self.engine = StratosEngine(secret=self.secret)
        self.cloud = CloudStratos()
        self.r_layer = RStratos()
        self.work_dir = Path('work/stratos')
        self.work_dir.mkdir(parents=True, exist_ok=True)
    
    async def execute_spec_file(self, spec_path: str) -> Dict[str, Any]:
        """Execute an operation spec file"""
        logger.info(f"Executing op spec: {spec_path}")
        
        # Validate first using R layer
        valid, validation_msg = self.r_layer.validate_spec(spec_path)
        if not valid:
            logger.error(f"Spec validation failed: {validation_msg}")
            return {
                'success': False,
                'error': f'Validation failed: {validation_msg}',
                'output': validation_msg
            }
        
        # Execute via engine
        success, output = self.engine.execute(spec_path)
        
        return {
            'success': success,
            'output': output,
            'spec_path': spec_path
        }
    
    async def quick_op(
        self,
        name: str,
        steps: list,
        operator: str = "TELEGRAM_USER"
    ) -> Dict[str, Any]:
        """Create and execute a quick operation from steps"""
        
        # Build spec
        ritual = Ritual()
        ritual.sign(self.secret)
        
        spec = OpSpec(
            ritual=ritual,
            meta={
                'name': name,
                'version': 'v1.0',
                'operator': operator
            },
            kernel={
                'purpose': ['quick.execution'],
                'rules': ['validate.steps'],
                'identity': ['telegram.op'],
                'structure': ['sequential'],
                'motion': ['outputs']
            },
            plan=steps
        )
        
        # Save to temp file
        spec_path = self.work_dir / f"{name.replace('.', '_')}.toml"
        spec.save(str(spec_path))
        
        # Execute
        return await self.execute_spec_file(str(spec_path))
    
    async def shell_op(self, command: str, operator: str) -> Dict[str, Any]:
        """Quick shell command execution"""
        steps = [{
            'type': 'shell',
            'id': 'cmd',
            'cmd': command
        }]
        
        return await self.quick_op(
            name='Shell.Command',
            steps=steps,
            operator=operator
        )
    
    async def llm_op(
        self,
        prompt: str,
        operator: str,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Quick LLM prompt execution"""
        # Wrap prompt in ritual format if not already
        if '::∎' not in prompt:
            prompt = f"///▙\n⟦⎊⟧\n\n{prompt}\n\n::∎"
        
        steps = [{
            'type': 'llm',
            'id': 'prompt',
            'prompt': prompt,
            'model': model or 'gpt-4'
        }]
        
        return await self.quick_op(
            name='LLM.Prompt',
            steps=steps,
            operator=operator
        )
    
    async def store_memory(self, key: str, value: Any) -> bool:
        """Store value in cloud.stratos memory"""
        return self.cloud.store_memory(key, value)
    
    async def recall_memory(self, key: str) -> Optional[Any]:
        """Recall value from cloud.stratos memory"""
        return self.cloud.recall_memory(key)
    
    async def generate_report(
        self,
        spec_path: str,
        output_path: str
    ) -> Dict[str, Any]:
        """Generate report using R layer"""
        success, output = self.r_layer.generate_report(spec_path, output_path)
        
        return {
            'success': success,
            'output': output,
            'report_path': output_path if success else None
        }


# Singleton instance
_executor = None

def get_executor() -> StratosExecutor:
    """Get global stratos executor instance"""
    global _executor
    if _executor is None:
        _executor = StratosExecutor()
    return _executor
