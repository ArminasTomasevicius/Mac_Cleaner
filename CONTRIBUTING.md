# Contributing to macOS Cache Cleaner

Thank you for your interest in contributing to macOS Cache Cleaner! 🎉

## How to Contribute

### Reporting Issues
- Use the GitHub Issues tab to report bugs or request features
- Include your macOS version and Python version
- Provide steps to reproduce the issue
- Include any error messages or screenshots

### Suggesting Enhancements
- Check existing issues to avoid duplicates
- Clearly describe the enhancement and its benefits
- Consider backward compatibility

### Code Contributions

#### Before You Start
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Test thoroughly on your macOS system

#### Development Guidelines
- Follow Python PEP 8 style guidelines
- Add comments for complex logic
- Maintain backward compatibility with Python 3.6+
- Test on different macOS versions if possible

#### Safety First
- **Never modify system-critical directories**
- Always test cache detection logic thoroughly
- Ensure new cache patterns are safe to delete
- Add appropriate safety checks for new features

#### Pull Request Process
1. Update the README.md if you add new features
2. Ensure your code follows the existing style
3. Test the interactive UI thoroughly
4. Submit a pull request with a clear description

### Adding New Cache Types

When adding support for new applications or cache types:

1. **Research First**: Ensure the cache is safe to delete
2. **Add to Safe Patterns**: Update the appropriate cache pattern lists
3. **Test Extensively**: Verify the application works after cache deletion
4. **Update Documentation**: Add the new cache type to README.md

### Code Structure

- `InteractiveUI`: Handles arrow-key navigation and real-time deletion
- `CacheCleaner`: Main logic for cache detection and deletion
- Safety checks are distributed throughout both classes

## Questions?

Feel free to open an issue for any questions about contributing!
