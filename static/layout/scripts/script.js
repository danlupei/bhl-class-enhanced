var userIsLoggedIn = true;

function signOut()
{
	var auth2 = gapi.auth2.getAuthInstance();
	auth2.signOut().then(function () {
	  console.log('User signed out.');
	});
	userIsLoggedIn = false;
	window.open("/", "_self");
}