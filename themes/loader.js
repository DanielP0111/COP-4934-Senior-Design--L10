//Any Javascript added to this file will inject and display on the main UI page. Use this file to override elements.

document.addEventListener("DOMContentLoaded", () => {

  const targetTitle = "Open WebUI";
  const newTitle = "DocTalk V2";
			
  const targetIntro = "Hello, User";
  const newIntro = "How can I help?";

  const targetAuth = "Sign in to Open WebUI"
  const newAuth = "Sign in to DocTalk V2"
			
	//replace agent greeting title
  function replaceIntro() {
	document.querySelectorAll("div.text-3xl.line-clamp-1").forEach((el) => {
	    const text = el.textContent.trim();
	    if (text === targetIntro) {
	        el.textContent = newIntro;
	    }
	});
  }

  // Replace sidebar title
  function replaceTitle() {
    document.querySelectorAll('a[href="/"] div').forEach((el) => {
      if (el.textContent.trim() === targetTitle) {
        el.textContent = newTitle;
		    el.style.color = "white";
		    el.style.setProperty("color", "white", "important");
      }
    });
  }

  // Replace signin page title
  function replaceAuth() {
    document.querySelectorAll('div.text-2xl.font-medium').forEach((el) => {
      if (el.textContent.trim() === targetAuth) {
        el.textContent = newAuth;
      }
    });
  }

  // Run replacements
  replaceTitle();
  replaceIntro();
  replaceAuth();

  // Persist changes
  const observer = new MutationObserver(() => {
    replaceTitle();
	  replaceIntro();
    replaceAuth();
  });

  observer.observe(document.body, { childList: true, subtree: true });

  // Change doc title
  const titleObserver = new MutationObserver(() => {
    if (document.title !== "DocTalk V2") {
      document.title = "DocTalk V2";
    }
  });

  titleObserver.observe(document.querySelector("title"), { childList: true });
});
