from django.db import models

# Create your models here.
class Post(models.Model):
    author = models.CharField(max_length=10, null=False)
    postname = models.CharField(max_length=50, null=False)
    contents = models.TextField()
    c_date = models.DateTimeField(auto_now_add=True)
    m_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

class Reply(models.Model):
    post_id = models.ForeignKey("Post", on_delete=models.CASCADE, db_column="post_id")
    author = models.CharField(max_length=10, null=False)
    contents = models.TextField()
    c_date = models.DateTimeField(auto_now_add=True)
    m_date = models.DateTimeField(auto_now=True)
    re_id = models.ForeignKey("self", on_delete=models.CASCADE, db_column="parent", null=True)
    depth = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)