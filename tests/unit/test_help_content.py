"""Unit tests for help content and formatting."""

import pytest
from click.testing import CliRunner

from vidscribe.cli import cli, transcribe, playlist, info, models


class TestHelpContentStructure:
    """Test help content structure and formatting."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_main_help_emojis_and_formatting(self):
        """Test main help contains proper emojis and formatting."""
        result = self.runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        output = result.output
        
        # Check for section emojis
        assert "🎬" in output  # Title emoji
        assert "🚀" in output  # Core capabilities
        assert "📖" in output  # Quick examples
        assert "⚡" in output  # Performance features
        assert "📁" in output  # Output formats
        
        # Check for bullet points
        assert "•" in output
        
        # Check for proper command references
        assert "vidscribe COMMAND --help" in output

    def test_all_commands_have_examples_section(self):
        """Test all commands have examples section."""
        commands = [transcribe, playlist, info, models]
        
        for command in commands:
            result = self.runner.invoke(command, ['--help'])
            assert result.exit_code == 0
            assert "📋 EXAMPLES:" in result.output

    def test_transcribe_help_comprehensive_examples(self):
        """Test transcribe help has comprehensive examples."""
        result = self.runner.invoke(transcribe, ['--help'])
        
        assert result.exit_code == 0
        output = result.output
        
        # Check for different example types
        examples = [
            "Basic YouTube video transcription",
            "Save to file with specific format",
            "Generate SRT subtitles",
            "Use larger model for better accuracy",
            "Force MLX acceleration",
            "Transcribe Spanish video in Spanish",
            "Translate any language to English",
            "Local video file with audio preservation",
            "JSON output with full metadata",
        ]
        
        for example in examples:
            assert example in output

    def test_playlist_help_url_types(self):
        """Test playlist help explains different URL types."""
        result = self.runner.invoke(playlist, ['--help'])
        
        assert result.exit_code == 0
        output = result.output
        
        # Check URL type explanations
        url_types = [
            "Playlist URLs: /playlist?list=PLxxxxxx",
            "Channel URLs: /@channelname or /channel/UCxxxxxx",
            "User URLs: /user/username",
        ]
        
        for url_type in url_types:
            assert url_type in output

    def test_model_sizes_consistency(self):
        """Test model sizes are consistent across help texts."""
        # Get model sizes from transcribe help
        transcribe_result = self.runner.invoke(transcribe, ['--help'])
        transcribe_output = transcribe_result.output
        
        # Get model sizes from models help
        models_result = self.runner.invoke(models, ['--help'])
        models_output = models_result.output
        
        # Check that both mention the same models
        model_names = ["tiny", "base", "small", "medium", "large"]
        
        for model in model_names:
            assert model in transcribe_output
            assert model in models_output

    def test_performance_features_mentioned(self):
        """Test performance features are properly highlighted."""
        result = self.runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        output = result.output
        
        performance_features = [
            "Auto-detects MLX acceleration on Apple Silicon",
            "Configurable model sizes",
            "Progress tracking with rich terminal output",
            "Automatic audio extraction from videos",
            "Optimized batch processing for playlists",
        ]
        
        for feature in performance_features:
            assert feature in output

    def test_output_formats_documented(self):
        """Test output formats are properly documented."""
        result = self.runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        output = result.output
        
        # Check format descriptions
        format_descriptions = [
            "text: Plain text transcription",
            "json: Full metadata + transcription",
            "csv: Spreadsheet-compatible format",
            "srt: Standard subtitle format",
            "vtt: WebVTT subtitle format",
        ]
        
        for description in format_descriptions:
            assert description in output


class TestHelpContentAccuracy:
    """Test help content accuracy and completeness."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_supported_video_formats_listed(self):
        """Test supported video formats are accurately listed."""
        result = self.runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        output = result.output
        
        # Check video format support
        assert "MP4, AVI, MOV, MKV, WebM support" in output

    def test_language_support_mentioned(self):
        """Test language support is properly mentioned."""
        result = self.runner.invoke(transcribe, ['--help'])
        
        assert result.exit_code == 0
        output = result.output
        
        # Check language support
        assert "99+ languages" in output
        assert "English (en), Spanish (es)" in output
        assert "French (fr), German (de)" in output

    def test_mlx_acceleration_documented(self):
        """Test MLX acceleration is properly documented."""
        commands = [cli, transcribe, playlist]
        
        for command in commands:
            result = self.runner.invoke(command, ['--help'])
            assert result.exit_code == 0
            assert "MLX" in result.output
            assert "Apple Silicon" in result.output

    def test_task_types_documented(self):
        """Test task types (transcribe/translate) are documented."""
        result = self.runner.invoke(transcribe, ['--help'])
        
        assert result.exit_code == 0
        output = result.output
        
        # Check task types
        assert "transcribe" in output.lower()
        assert "translate" in output.lower()
        assert "Translate any language to English" in output

    def test_csv_output_format_explained(self):
        """Test CSV output format is properly explained for playlist."""
        result = self.runner.invoke(playlist, ['--help'])
        
        assert result.exit_code == 0
        output = result.output
        
        # Check CSV format explanation
        assert "CSV file with columns: Title, URL, Duration, Transcription, Error" in output


class TestHelpUsabilityFeatures:
    """Test help usability and user guidance features."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_use_cases_provided(self):
        """Test use cases are provided for info command."""
        result = self.runner.invoke(info, ['--help'])
        
        assert result.exit_code == 0
        output = result.output
        
        use_cases = [
            "Verify video accessibility before transcription",
            "Check video duration for processing time estimates",
            "Confirm correct video before batch processing",
        ]
        
        for use_case in use_cases:
            assert use_case in output

    def test_performance_tips_provided(self):
        """Test performance tips are provided for playlist command."""
        result = self.runner.invoke(playlist, ['--help'])
        
        assert result.exit_code == 0
        output = result.output
        
        tips = [
            "Use 'tiny' or 'base' models for faster batch processing",
            "Enable MLX acceleration on Apple Silicon",
            "Use --limit for testing on large channels",
        ]
        
        for tip in tips:
            assert tip in output

    def test_model_selection_guidance(self):
        """Test model selection guidance is provided."""
        result = self.runner.invoke(models, ['--help'])
        
        assert result.exit_code == 0
        output = result.output
        
        guidance = [
            "tiny: Quick drafts, testing, low-resource environments",
            "base: General use, good balance of speed/accuracy (recommended)",
            "small: Better accuracy when you have more time/resources",
            "medium: High accuracy for important transcriptions",
            "large: Maximum accuracy for critical/professional use",
        ]
        
        for guide in guidance:
            assert guide in output

    def test_practical_examples_with_real_urls(self):
        """Test examples use realistic URLs and paths."""
        result = self.runner.invoke(transcribe, ['--help'])
        
        assert result.exit_code == 0
        output = result.output
        
        # Check for realistic examples
        assert "youtu.be" in output
        assert "VIDEO_URL" in output
        assert "/path/video.mp4" in output
        assert ".srt" in output
        assert ".json" in output

    def test_command_cross_references(self):
        """Test commands properly reference each other."""
        result = self.runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        output = result.output
        
        # Check for command cross-references
        assert "vidscribe COMMAND --help" in output
        
        # Check that all main commands are mentioned
        commands = ["transcribe", "playlist", "info", "models"]
        for command in commands:
            assert command in output


class TestHelpAccessibility:
    """Test help accessibility and readability."""

    def setup_method(self):
        """Set up test runner."""
        self.runner = CliRunner()

    def test_help_text_not_too_verbose(self):
        """Test help text is comprehensive but not overwhelming."""
        result = self.runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        output = result.output
        
        # Check that help is structured with clear sections
        sections = [
            "🚀 CORE CAPABILITIES:",
            "📖 QUICK EXAMPLES:",
            "⚡ PERFORMANCE FEATURES:",
            "📁 OUTPUT FORMATS:",
        ]
        
        for section in sections:
            assert section in output
        
        # Help should not be excessively long (rough check)
        lines = output.split('\n')
        assert len(lines) < 100  # Reasonable upper bound

    def test_consistent_formatting_across_commands(self):
        """Test consistent formatting across all command helps."""
        commands = [transcribe, playlist, info, models]
        
        for command in commands:
            result = self.runner.invoke(command, ['--help'])
            assert result.exit_code == 0
            output = result.output
            
            # Check for consistent section markers
            assert "📋 EXAMPLES:" in output
            
            # Check for proper bullet point usage
            if "•" in output:
                # If bullets are used, they should be consistent
                lines_with_bullets = [line for line in output.split('\n') if '•' in line]
                assert len(lines_with_bullets) > 0

    def test_help_readable_without_emojis(self):
        """Test help is still readable if emojis are stripped."""
        result = self.runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        output = result.output
        
        # Remove emojis and check readability
        import re
        no_emoji = re.sub(r'[^\w\s\-\.\:\(\)\[\]\,\/\@\#\?\=\&\;]', '', output)
        
        # Should still contain key information
        assert "Vidscribe" in no_emoji
        assert "YouTube" in no_emoji
        assert "EXAMPLES" in no_emoji
        assert "vidscribe transcribe" in no_emoji