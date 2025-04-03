# EromeAPI
A simple erome wrapper

# What this wrapper can do?

- [x] Access url content
- [x] Search using keywords
- [x] Access album content
- [ ] Access your account
- [ ] Upload files
- [ ] Edit posts
- [ ] Comment on any post
- [x] Get the explore content

# Example code:
```
from api import Api

api = Api()

api.get_all_album_data("keyword")

api.get_album_content("album code") # This will return all url videos and photos. Example: api.get_album_content("RHoERFQP")

api.get_content("url") # This will return all the bytes of the url. Example: api.get_content("https://s71.erome.com/2901/RHoERFQP/thumbs/3c3bTKup.jpeg?v=1721382642")

api.get_explore()
```
