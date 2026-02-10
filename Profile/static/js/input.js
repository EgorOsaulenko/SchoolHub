const inputTag = document.querySelectorAll("input")

inputTag.forEach(function(tag) {
    tag.setAttribute("class", "form-control")
})

const select = document.querySelector("select")
select.setAttribute("class", "form-control")

const textArea = document.querySelector("textarea")
textArea.setAttribute("class", "form-control")