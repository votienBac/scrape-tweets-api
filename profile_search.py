import snscrape.modules.twitter as sntwitter
class ProfileSearch:
    def getProfileByUsername(self, username):
        profile = sntwitter.TwitterUserScraper(username)
        user = profile.entity
        if user is None:
            return None
        user_dict = {
            'id': str(user.id),
            'username': user.username,
            'name': user.displayname,
            'url': user.url,
            'description': user.rawDescription,
            'verified': user.verified,
            'followers_count': user.followersCount,
            'friends_count': user.friendsCount,
            'listed_count': user.listedCount,
            'favourites_count': user.favouritesCount,
            'statuses_count': user.statusesCount,
            'media_count': user.mediaCount,
            'statuses_count': user.statusesCount,
            'profile_image_url': user.profileImageUrl,
            'profile_banner_url': user.profileBannerUrl,
            'created_date': user.created.strftime('%Y-%m-%d %H:%M:%S')
        }
        return user_dict                                                                                                                                                                                                           