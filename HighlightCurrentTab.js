document.addEventListener("headerLoaded", () =>
{
   HighlightCurrentTab();
});

function HighlightCurrentTab()
{
   const currentPath = window.location.pathname.split("/").pop();
   document.querySelectorAll("a").forEach(link =>
   {
      const linkPath = link.getAttribute("href");
      console.log("linkPath: " + linkPath);
      console.log("currentPath: " + currentPath);
      if (linkPath === currentPath)
      {
         link.classList.add("active");
      }
   });
}

