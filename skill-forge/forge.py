import os
import json
import shutil
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class SkillForge:
    """
    Main skill generation engine for GEMINI X HERMES v2.
    Handles creation, templating, and logging of AI skills.
    """

    def __init__(
        self, 
        output_dir: Optional[str] = None, 
        global_skills_dir: Optional[str] = None
    ) -> None:
        # Resolve base directory relative to this script
        self.base_dir = Path(__file__).parent.resolve()
        
        # Set output directory
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = self.base_dir / "forged-skills"
            
        # Set global skills directory
        if global_skills_dir:
            self.global_skills_dir = Path(global_skills_dir)
        else:
            self.global_skills_dir = Path.home() / ".gemini" / "config" / "skills"
            
        self.log_file = self.base_dir / "forge-log.json"
        self.templates_dir = self.base_dir / "templates"
        
        # Ensure directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.global_skills_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize JSON log file if it doesn't exist
        if not self.log_file.exists():
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)

    def forge_skill(
        self, 
        name: str, 
        description: str, 
        workflow_steps: List[str], 
        category: str, 
        tags: List[str]
    ) -> Path:
        """
        Generate a complete SKILL.md for a given skill.
        
        Args:
            name (str): The name of the skill.
            description (str): Description of what the skill does.
            workflow_steps (List[str]): List of steps for the skill.
            category (str): Skill category (e.g., 'debugging', 'setup', 'workflow').
            tags (List[str]): Tags related to the skill.
            
        Returns:
            Path: Path to the generated SKILL.md file.
        """
        content = self._generate_skill_content(name, description, workflow_steps, category, tags)
        
        skill_dir = self.output_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        skill_file = skill_dir / "SKILL.md"
        with open(skill_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        # Log entry for the forged skill
        log_entry = {
            "id": f"forge_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "skill_name": name,
            "category": category,
            "tags": tags,
            "source_workflow": description,
            "installed_globally": False
        }
        self._save_forge_log(log_entry)
        
        return skill_file

    def install_globally(self, skill_name: str) -> bool:
        """
        Copy a forged skill to the global skills directory.
        
        Args:
            skill_name (str): The name of the skill to install.
            
        Returns:
            bool: True if installation was successful.
            
        Raises:
            FileNotFoundError: If the skill does not exist in the forged skills directory.
        """
        source_dir = self.output_dir / skill_name
        target_dir = self.global_skills_dir / skill_name
        
        if not source_dir.exists():
            raise FileNotFoundError(f"Skill '{skill_name}' not found in forged skills directory.")
            
        # Copy to global directory
        shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
        
        # Update log to reflect global installation
        logs = self.get_forge_log()
        updated = False
        for entry in logs:
            if entry.get("skill_name") == skill_name:
                entry["installed_globally"] = True
                updated = True
                
        if updated:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2)
                
        return True

    def list_forged_skills(self) -> List[str]:
        """
        List all generated skills in the output directory.
        
        Returns:
            List[str]: A list of forged skill names.
        """
        skills = []
        if self.output_dir.exists():
            for entry in self.output_dir.iterdir():
                if entry.is_dir() and (entry / "SKILL.md").exists():
                    skills.append(entry.name)
        return skills

    def get_forge_log(self) -> List[Dict[str, Any]]:
        """
        Return history of forged skills.
        
        Returns:
            List[Dict[str, Any]]: List of log entries.
        """
        if not self.log_file.exists():
            return []
        with open(self.log_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _generate_skill_content(
        self, 
        name: str, 
        description: str, 
        workflow_steps: List[str], 
        category: str, 
        tags: List[str]
    ) -> str:
        """
        Template engine to generate skill markdown content.
        """
        template_file = self.templates_dir / f"{category}.md"
        
        if not template_file.exists():
            # Fallback to the workflow template if category template is not found
            template_file = self.templates_dir / "workflow.md"
            if not template_file.exists():
                return self._fallback_template(name, description, workflow_steps, category, tags)
                
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()
            
        steps_str = "\n".join([f"{i+1}. {step}" for i, step in enumerate(workflow_steps)])
        tags_str = ", ".join(tags)
        
        # Replace placeholders
        content = template.replace("{{name}}", name)
        content = content.replace("{{description}}", description)
        content = content.replace("{{steps}}", steps_str)
        content = content.replace("{{category}}", category)
        content = content.replace("{{tags}}", tags_str)
        
        # Default text for common sections
        content = content.replace("{{pitfalls}}", "- Belum ada catatan (No pitfalls recorded yet)")
        content = content.replace("{{verification}}", "- [ ] Langkah-langkah berhasil dieksekusi (Steps executed successfully)")
        
        return content
        
    def _fallback_template(
        self, 
        name: str, 
        description: str, 
        workflow_steps: List[str], 
        category: str, 
        tags: List[str]
    ) -> str:
        """Provide a fallback template if physical templates are missing."""
        steps_str = "\n".join([f"{i+1}. {step}" for i, step in enumerate(workflow_steps)])
        tags_str = ", ".join(tags)
        
        return f"""---
name: {name}
description: {description}
category: {category}
tags: [{tags_str}]
---

# Overview
{description}

## When To Use
Gunakan skill ini ketika menghadapi situasi terkait {category}.

## Step-by-Step Protocol
{steps_str}

## Common Pitfalls
- Belum ada catatan (No pitfalls recorded yet)

## Verification
- [ ] Langkah-langkah berhasil dieksekusi (Steps executed successfully)
"""

    def _save_forge_log(self, entry: Dict[str, Any]) -> None:
        """Append a new entry to the forge log file."""
        logs = self.get_forge_log()
        logs.append(entry)
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2)

if __name__ == "__main__":
    print("Memulai Auto Skill Forge (Starting Auto Skill Forge)...")
    forge = SkillForge()
    
    skill_name = "react-hooks-debugging"
    print(f"Membangun skill baru: {skill_name}")
    
    skill_path = forge.forge_skill(
        name=skill_name,
        description="Fixed useEffect cleanup in KanbanBoard",
        workflow_steps=[
            "Identify the useEffect hook causing issues.",
            "Check for missing dependency arrays.",
            "Add cleanup function returning from the hook.",
            "Test component unmount behavior."
        ],
        category="debugging",
        tags=["react", "hooks", "useState"]
    )
    
    print(f"Skill berhasil dibuat di (Skill successfully created at): {skill_path}")
    print(f"Daftar skills (List of skills): {forge.list_forged_skills()}")
    
    print("Mencoba instalasi global... (Attempting global installation...)")
    try:
        forge.install_globally(skill_name)
        print("Berhasil! (Success!)")
    except Exception as e:
        print(f"Gagal instalasi global (Failed global install): {e}")
