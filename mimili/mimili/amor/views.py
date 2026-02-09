from django.shortcuts import render


def home(request):
	"""Render the homepage that mimics the provided design."""
	return render(request, "index.html")

def playlists(request):
    """Render the playlists page."""
    return render(request, "playlists.html")

def diary(request):
    """Render the dear diary page."""
    return render(request, "diary.html")

def proposal(request):
    """Render the proposal page."""
    return render(request, "proposal.html")

def carta(request):
    """Render the menu / carta page."""
    return render(request, "carta.html")

