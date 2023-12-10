from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login
from .forms import UserForm
from .models import Post, Reply
from django.contrib.auth.decorators import login_required


def getReply(post_id):
    l = []
    r = Reply.objects.filter(post_id=post_id)
    for i in r:
        if not i.re_id:
            l.append(i)
        else:
            b = False
            for ii in l[l.index(i.re_id)+1:]:
                if ii.depth <= i.re_id.depth:
                    l.insert(l.index(ii), i)
                    b = True
                    break
            if not b:
                l.append(i)
    return l

# Create your views here.


def home(request):
    postlist = Post.objects.order_by('-c_date').values()

    return render(request, "home.html", {'postlist': postlist})


def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = UserForm()
    return render(request, 'signup.html', {'form': form})


def write(request):
    if not request.user.is_authenticated:
        return redirect("/login/")
    else:
        if request.method == "POST":
            b = Post(author=request.user.get_username(), postname=request.POST['postname'],
                     contents=request.POST['contents'])
            b.save()
            return redirect("/")
        else:
            return render(request, "write.html")


def modify(request, post_id):
    post = Post.objects.get(id=post_id)
    if not request.user.is_authenticated:
        return redirect("/login/")
    else:
        if post.author != request.user.get_username():
            return redirect("/post/" + str(post_id))
        else:
            if request.method == "POST":
                post.postname = request.POST['postname']
                post.contents = request.POST['contents']
                post.save()
                return redirect("/post/" + str(post_id))
            else:
                return render(request, "modify.html", {'post': post, 'post_id': post_id})


def delete(request, post_id):
    post = Post.objects.get(id=post_id)
    if not request.user.is_authenticated:
        return redirect("/login/")
    else:
        if post.author != request.user.get_username():
            return redirect("/post/" + str(post_id))
        else:
            post.delete()
            return redirect("/")


def post(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.method == "POST" and request.POST['submit'] == "reply":
        if not request.user.is_authenticated:
            return redirect("/login/")
        else:
            r = Reply(post_id=post, author=request.user.get_username(), contents=request.POST['contents'])
            r.save()
    reply = getReply(post_id)
    return render(request, "post.html", {'post': post, 'reply': reply})


def rd(request, reply_id):
    r = Reply.objects.get(id=reply_id)
    p_id = r.post_id
    if not request.user.is_authenticated:
        return redirect("/login/")
    else:
        if r.author != request.user.get_username():
            return redirect("/post/" + str(p_id))
        else:
            r.delete()
            return redirect("/post/" + str(p_id))


def rm(request, reply_id):
    r = Reply.objects.get(id=reply_id)
    p_id = r.post_id
    if not request.user.is_authenticated:
        return redirect("/login/")
    else:
        if r.author != request.user.get_username():
            return redirect("/post/" + str(p_id))
        else:
            r.contents = request.POST['contents']
            r.save()
            return redirect("/post/" + str(p_id))


def rr(request, reply_id):
    reply = Reply.objects.get(id=reply_id)
    post_id = reply.post_id
    if not request.user.is_authenticated:
        return redirect("/login/")
    else:
        rereply = Reply(post_id=post_id, author=request.user.get_username(), contents=request.POST['contents'], re_id=reply, depth=reply.depth+1)
        rereply.save()
    return redirect("/post/"+str(post_id))


def mypage(request):
    return HttpResponse("mypage")
