SetElementHTML("header", "/Templates/Header.html");
SetElementHTML("footer", "/Templates/Footer.html");

function SetElementHTML(elementId, htmlFileName)
{
   fetch(htmlFileName)
      .then(response => response.text())
      .then(html =>
      {
         document.getElementById(elementId).innerHTML = html;
      });
}

