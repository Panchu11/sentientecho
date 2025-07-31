# Contributing to SentientEcho 🤝

**Thank you for your interest in contributing to SentientEcho!**

This guide will help you get started with contributing to the project, whether you're fixing bugs, adding features, or improving documentation.

## 🎯 **Ways to Contribute**

### **🐛 Bug Reports**
- Report bugs through GitHub Issues
- Include detailed reproduction steps
- Provide environment information
- Attach relevant logs or screenshots

### **✨ Feature Requests**
- Suggest new features or improvements
- Explain the use case and benefits
- Discuss implementation approaches
- Consider backward compatibility

### **📝 Documentation**
- Improve existing documentation
- Add examples and tutorials
- Fix typos and clarify instructions
- Translate documentation

### **💻 Code Contributions**
- Fix bugs and issues
- Implement new features
- Improve performance
- Add tests and improve coverage

### **🧪 Testing**
- Write and improve tests
- Test new features and bug fixes
- Report testing results
- Improve test coverage

## 🚀 **Getting Started**

### **1. Fork and Clone**
```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/sentientecho.git
cd sentientecho

# Add upstream remote
git remote add upstream https://github.com/Panchu11/sentientecho.git
```

### **2. Development Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Validate setup
python setup.py
```

### **3. Create Feature Branch**
```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number
```

## 📋 **Development Guidelines**

### **Code Style**
- Follow PEP 8 for Python code
- Use type hints for all functions
- Write descriptive variable and function names
- Add docstrings to all public functions
- Keep functions focused and small

### **Example Code Style**:
```python
async def process_query(self, query: str, session_id: str) -> QueryResult:
    """
    Process a user query and return enhanced results.
    
    Args:
        query: The user's natural language query
        session_id: Unique session identifier
        
    Returns:
        QueryResult containing processed content and metadata
        
    Raises:
        ValueError: If query is invalid
        APIError: If external API calls fail
    """
    logger.info("Processing query for session %s", session_id)
    
    # Validate input
    if not query or len(query.strip()) == 0:
        raise ValueError("Query cannot be empty")
    
    # Process query
    try:
        result = await self._internal_process(query)
        return result
    except Exception as e:
        logger.exception("Failed to process query")
        raise APIError(f"Query processing failed: {e}")
```

### **Commit Messages**
Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(providers): add LinkedIn content provider

Add new LinkedIn provider to fetch professional content
and discussions. Includes rate limiting and error handling.

Closes #123

fix(cache): resolve memory leak in cache cleanup

The cache cleanup process was not properly releasing
memory for expired entries, causing gradual memory growth.

test(integration): add tests for new Twitter provider

Add comprehensive integration tests covering success
and failure scenarios for the Twitter content provider.
```

## 🧪 **Testing Requirements**

### **Test Coverage**
- All new code must include tests
- Aim for >90% test coverage
- Include both unit and integration tests
- Test error conditions and edge cases

### **Running Tests**
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src tests/

# Run specific test file
python -m pytest tests/test_integration.py

# Run tests with verbose output
python -m pytest -v tests/
```

### **Writing Tests**
```python
import pytest
from unittest.mock import AsyncMock, patch
from src.providers.reddit_provider import RedditProvider

class TestRedditProvider:
    @pytest.fixture
    def reddit_provider(self):
        return RedditProvider(api_key="test_key")
    
    @pytest.mark.asyncio
    async def test_search_posts_success(self, reddit_provider):
        """Test successful post search."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.json.return_value = {"data": {"children": []}}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            posts = await reddit_provider.search_posts(["python"])
            assert isinstance(posts, list)
    
    @pytest.mark.asyncio
    async def test_search_posts_api_error(self, reddit_provider):
        """Test handling of API errors."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = aiohttp.ClientError("API Error")
            
            with pytest.raises(APIError):
                await reddit_provider.search_posts(["python"])
```

## 📝 **Documentation Standards**

### **Code Documentation**
- Add docstrings to all public functions and classes
- Include parameter types and descriptions
- Document return values and exceptions
- Provide usage examples for complex functions

### **README Updates**
- Update README.md for new features
- Add configuration options
- Include usage examples
- Update installation instructions if needed

### **API Documentation**
- Update API.md for new endpoints
- Include request/response examples
- Document error codes and responses
- Add authentication requirements

## 🔍 **Pull Request Process**

### **Before Submitting**
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main

### **Pull Request Template**
```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings or errors introduced

## Related Issues
Closes #issue_number
```

### **Review Process**
1. **Automated Checks**: CI/CD pipeline runs tests
2. **Code Review**: Maintainers review code quality
3. **Testing**: Manual testing of new features
4. **Documentation Review**: Check documentation updates
5. **Approval**: At least one maintainer approval required

## 🐛 **Bug Report Template**

```markdown
## Bug Description
A clear and concise description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
A clear description of what you expected to happen.

## Actual Behavior
A clear description of what actually happened.

## Environment
- OS: [e.g. Ubuntu 20.04, Windows 10, macOS 12]
- Python Version: [e.g. 3.9.7]
- SentientEcho Version: [e.g. 1.0.0]
- Docker Version: [if using Docker]

## Additional Context
- Error logs
- Screenshots
- Configuration files (remove sensitive data)
- Any other relevant information
```

## ✨ **Feature Request Template**

```markdown
## Feature Description
A clear and concise description of the feature you'd like to see.

## Problem Statement
What problem does this feature solve? What use case does it address?

## Proposed Solution
Describe the solution you'd like to see implemented.

## Alternative Solutions
Describe any alternative solutions or features you've considered.

## Additional Context
- Examples from other projects
- Mockups or diagrams
- Implementation ideas
- Potential challenges
```

## 🔒 **Security Guidelines**

### **Security Issues**
- **DO NOT** open public issues for security vulnerabilities
- Email security issues to: [security contact]
- Include detailed reproduction steps
- Allow time for fix before public disclosure

### **Secure Coding**
- Never commit API keys or secrets
- Validate all user inputs
- Use parameterized queries
- Follow OWASP guidelines
- Implement proper error handling

## 🎉 **Recognition**

### **Contributors**
All contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation
- GitHub contributors list

### **Types of Contributions**
- Code contributions
- Documentation improvements
- Bug reports and testing
- Feature suggestions
- Community support

## 📞 **Getting Help**

### **Questions**
- Check existing documentation first
- Search existing issues
- Ask in GitHub Discussions
- Join community chat

### **Stuck?**
- Review DEVELOPER_GUIDE.md
- Check TROUBLESHOOTING.md
- Ask for help in your pull request
- Reach out to maintainers

## 📋 **Code of Conduct**

### **Our Standards**
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences
- Show empathy towards other community members

### **Unacceptable Behavior**
- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Publishing private information
- Other unprofessional conduct

## 🚀 **Development Workflow**

### **Typical Workflow**
1. **Issue Discussion**: Discuss feature/bug in GitHub Issues
2. **Fork & Branch**: Create feature branch from main
3. **Develop**: Write code following guidelines
4. **Test**: Add tests and ensure all tests pass
5. **Document**: Update relevant documentation
6. **Pull Request**: Submit PR with clear description
7. **Review**: Address feedback from maintainers
8. **Merge**: PR merged after approval

### **Release Process**
- Features merged to `main` branch
- Regular releases from `main`
- Semantic versioning (MAJOR.MINOR.PATCH)
- Release notes with changelog
- Tagged releases on GitHub

---

**Thank you for contributing to SentientEcho! Your contributions help make this project better for everyone.** 🙏
