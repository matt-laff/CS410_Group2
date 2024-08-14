document.querySelectorAll(".editable").forEach((element) => {
  let oldpath = element.innerText;

  element.addEventListener("focus", (event) => {
    oldpath = event.target.innerText;
  });

  element.addEventListener("blur", (event) => {
    const newpath = event.target.innerText;
    if (oldpath !== newpath) {
    event.target.style.color = "purple";
    event.target.innerHTML = `<b style="border: 2px solid #ddd; padding: 5px;">${newpath}</b>`;
      console.log(`Filename changed from "${oldpath}" to "${newpath}"`);

      fetch("/edit", {
        method: "POST",
        body: JSON.stringify({ oldpath: oldpath, newpath: newpath }),
        headers: {
          "Content-Type": "application/json",
        },
      });
    }
  });
});
