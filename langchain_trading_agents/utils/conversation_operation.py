import os
import asyncio
import aiofiles
from datetime import datetime
from loguru import logger
from langchain_trading_agents.contant import ConversationData


class LangchainConversationOperation:
    _write_lock = asyncio.Lock()
    _shutdown = False  # Shutdown flag

    def __init__(self):
        pass

    @classmethod
    def set_shutdown(cls):
        """Set shutdown flag to prevent new operations"""
        cls._shutdown = True

    async def a_save(self, data: ConversationData | dict, fold_path=None):
        """
        Asynchronously save conversation record to Markdown file with global write protection

        Args:
            data: ConversationData instance or dictionary data
            fold_path: Specified folder path, use default path if None
        """
        try:
            # Check shutdown status
            if self._shutdown:
                logger.warning("Skipping save operation due to shutdown")
                return

            # Convert data to ConversationData instance
            conversation: ConversationData = ConversationData(**data) if isinstance(data, dict) else data

            # 使用全局锁，同时只能有一个文件写入操作
            async with self._write_lock:
                # Double-check shutdown status after acquiring lock
                if self._shutdown:
                    logger.warning("Skipping save operation due to shutdown after lock acquisition")
                    return

                # Determine save directory
                if fold_path is None:
                    # Use conversation_record folder under current working directory
                    base_dir = os.getcwd()
                    save_dir = os.path.join(base_dir, "conversation_record")
                else:
                    save_dir = fold_path

                # Ensure directory exists
                os.makedirs(save_dir, exist_ok=True)

                # Build file path
                filename = f"{conversation.conversation_id}.md"
                file_path = os.path.join(save_dir, filename)

                # Generate Markdown content
                md_content = self._generate_markdown_content(conversation)+"\n---"

                # Try asynchronous write first, fallback to synchronous if event loop is shutting down
                try:
                    async with aiofiles.open(file_path, 'a', encoding='utf-8') as f:
                        await f.write(md_content + "\n\n")
                except RuntimeError as e:
                    if 'shutdown' in str(e).lower() or 'cannot schedule' in str(e).lower():
                        logger.warning("Event loop shutting down, using synchronous file write as fallback")
                        # Fallback to synchronous file write
                        try:
                            with open(file_path, 'a', encoding='utf-8') as f:
                                f.write(md_content + "\n\n")
                            logger.info(
                                f"Successfully saved conversation {conversation.conversation_id} using synchronous fallback")
                        except Exception as sync_e:
                            logger.error(
                                f"Failed to save conversation {conversation.conversation_id} even with synchronous fallback: {sync_e}")
                    else:
                        raise

        except Exception as e:
            # Log error but don't re-raise to prevent task exception
            logger.error(f"Error saving conversation: {e}")
            if "shutdown" not in str(e).lower():
                logger.exception("Full traceback:")

    def _generate_markdown_content(self, conv: ConversationData) -> str:
        """Generate formatted Markdown content"""

        try:
            # Format timestamp
            try:
                timestamp = datetime.fromisoformat(conv.timestamp)
                formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S%z")
            except:
                formatted_time = conv.timestamp

            # Determine icons and styles based on message type
            type_icons = {
                "ai": "🤖",
                "human": "👤",
                "system_prompt": "⚙️",
                "call_tool": "🔧",
                "tools": "🛠️",
                "error": "❌",
                "other": "📝"
            }

            icon = type_icons.get(conv.conv_message_type.lower(), "📝")

            # Build basic information
            md_lines = [
                #"---",
                f"## {icon} {conv.conv_message_type.upper()}",
                f"**Time**: {formatted_time}",
                f"**Department**: {conv.department}",
                f"**Nickname**: {conv.nickname}",
                ""
            ]

            # Add LLM model configuration information (if exists)
            if conv.llm_model_config:
                md_lines.append("### 🔧 LLM Model Configuration")
                if isinstance(conv.llm_model_config, dict):
                    for key, value in conv.llm_model_config.items():
                        md_lines.append(f"- **{key}**: {value}")
                else:
                    md_lines.append(f"```\n{conv.llm_model_config}\n```")
                md_lines.append("")

            # Add message content - conditionally use code block format for specific message types
            # Add message content - conditionally use code block format for specific message types
            if conv.conv_message_type.lower() in ['call_tool', 'tools']:
                md_lines.extend([
                    "### 💬 Content",
                    "",
                    "```",
                    conv.content,
                    "```",
                    ""
                ])
            elif conv.conv_message_type.lower() == 'system_prompt':
                md_lines.extend([
                    "### 💬 Content",
                    "",
                    "<details>",
                    "  <summary>📋 System Prompt (Click to expand)</summary>",
                    "",
                    conv.content,
                    "",
                    "</details>",
                    ""
                ])
            else:
                md_lines.extend([
                    "### 💬 Content",
                    "",
                    conv.content,
                    ""
                ])

            # Add usage metadata (if exists and not empty)
            if conv.usage_metadata:
                md_lines.append("### 📊 Usage Statistics")
                md_lines.append(f"**Department**: {conv.department}")
                md_lines.append(f"**Nickname**: {conv.nickname}")
                md_lines.append("")

                if isinstance(conv.usage_metadata, dict):
                    # Format dictionary type usage_metadata
                    md_lines.append("| Metric | Value |")
                    md_lines.append("|--------|-------|")
                    for key, value in conv.usage_metadata.items():
                        md_lines.append(f"| {key} | {value} |")
                elif isinstance(conv.usage_metadata, (list, str)):
                    # Handle list or string types
                    md_lines.append("```")
                    if isinstance(conv.usage_metadata, list):
                        for item in conv.usage_metadata:
                            md_lines.append(str(item))
                    else:
                        md_lines.append(str(conv.usage_metadata))
                    md_lines.append("```")
                md_lines.append("")

            return "\n".join(md_lines)

        except Exception as e:
            logger.error(f"Error generating markdown content: {e}")
            return f"Error generating content for conversation {getattr(conv, 'conversation_id', 'unknown')}: {str(e)}"