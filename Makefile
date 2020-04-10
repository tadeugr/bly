abc:
	echo $(ARGS)
	curl \
		-X POST 'http://localhost:7700/indexes' \
		--data '{
			"uid": "$(ARGS)",
			"primaryKey": "movie_id"
		}'