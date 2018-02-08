DIRTY_FILES=$$(git status --porcelain --untracked-files=all)


commits:
	@for path in $(DIRTY_FILES); do \
		git add $$path; \
		git commit -sm "Update $$path"; \
	done; \
	git add .; \
	git commit --sm 'refactor codebase'; \
	git push;