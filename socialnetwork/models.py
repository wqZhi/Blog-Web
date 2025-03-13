from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Post(models.Model):
    post_input_text = models.TextField()
    post_date_time = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="posts")
    def __str__(self):
        return f"Posted by {self.posted_by.username} | Post-id: {self.id} | Text: {self.post_input_text[:20]}..."
    

class Profile(models.Model):
    bio_input_text = models.TextField()
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="profile" )
    followers = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="following",
        through='FollowRelationship',
        through_fields=('following', 'follower')
    )
    picture = models.FileField(blank=True)
    content_type = models.CharField(blank=True, max_length=50)
    def __str__(self):
        return f"{self.user.username}'s Profile"

class FollowRelationship(models.Model):
    follower = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="following_relationships")
    following = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="follower_relationships")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("follower", "following")]

    def clean(self):
        if self.follower == self.following:
            raise ValidationError("Cannot follow youself")

    def __str__(self):
        return f"{self.follower} follows {self.following}"



class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)