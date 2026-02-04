# Communication Protocol for Human-AI-AI Collaboration

## Project: Phoenix Civic Simulation Engine

### Team Structure
- **Ross Sakowski** (Human) - Project lead, domain expertise, final decisions
- **Astra** (AI Agent) - Primary architect, vision, complex reasoning
- **Claude Code** (AI Assistant) - Implementation, testing, optimization

### Communication Channels

#### 1. GitHub Issues
- **Astra → Claude**: Create issues with detailed specifications
- **Claude → Astra**: Comment on issues with questions/updates
- **Labels**: Use labels to indicate task type and priority

#### 2. Pull Request Comments
- **Astra**: Leave detailed code review comments
- **Claude**: Respond to feedback, explain changes

#### 3. Commit Messages
- **Detailed context**: Always explain the "why" behind changes
- **Cross-references**: Link to related issues/discussions

### Task Delegation Protocol

#### Astra's Role (Token-Intensive Tasks)
- Architecture design
- Complex algorithm development
- Human-AI collaboration protocols
- Philosophical/ethical considerations
- High-level vision and strategy

#### Claude's Role (Implementation Tasks)
- Writing tests
- Code optimization and refactoring
- Documentation improvements
- Bug fixes
- Data pipeline implementation
- Performance profiling

### Communication Templates

#### For Astra → Claude (Issue Creation)
```
Title: [IMPLEMENT] Feature Name
Priority: High/Medium/Low

## Context
[Explain why this is needed, link to related work]

## Specification
[Detailed technical requirements]

## Acceptance Criteria
- [ ] Test 1
- [ ] Test 2

## Notes
[Any special considerations]

## Related
- Issue #123
- PR #456
```

#### For Claude → Astra (Implementation Updates)
```
## Implementation Summary
[What was built/changed]

## Key Decisions
[Any important choices made]

## Testing
[How it was tested]

## Questions
[Any clarifications needed]
```

### Cost Optimization Guidelines

#### Use Claude Code For:
- Writing extensive test suites
- Refactoring existing code
- Performance optimization
- Documentation writing
- Code review and suggestions
- Implementation of well-defined features

#### Use Astra For:
- Initial architecture design
- Complex algorithm development
- Human-AI interaction design
- Ethical considerations
- High-level strategic decisions
- Novel problem-solving

### Project-Specific Notes

#### Phoenix CSE Context
- Focus on heat vulnerability and urban planning
- Prioritize public health outcomes
- Consider ethical implications of interventions
- Maintain human-AI collaboration principles
- Document decision-making rationale

#### Code Quality Standards
- Write comprehensive tests
- Document all public APIs
- Follow PEP 8 style guidelines
- Include docstrings for all functions
- Consider edge cases and error handling

### Communication Best Practices

1. **Be specific**: Clear, detailed requirements
2. **Provide context**: Explain the "why" behind tasks
3. **Link related work**: Cross-reference issues and PRs
4. **Ask questions**: Clarify before implementing
5. **Document decisions**: Record reasoning for future reference

### Emergency Protocols

If urgent issues arise:
1. Create GitHub issue with "URGENT" label
2. Provide clear reproduction steps
3. Suggest potential solutions if known
4. Tag relevant team members

---

**Remember**: We're building this together for the common good. Every line of code should serve the mission of preventing heat-related deaths in Phoenix.