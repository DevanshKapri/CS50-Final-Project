document.addEventListener('DOMContentLoaded', function () {
    
    let corrects = document.querySelectorAll('.correct');
    let incorrects = document.querySelectorAll('.incorrect');
    let feeds = document.querySelectorAll('#f1');

    for (let i = 0; i < corrects.length; i++) {
        corrects[i].addEventListener('click', function () {
            corrects[i].style.backgroundColor = '#00FF00';
            incorrects[i].style.backgroundColor = '#FF0000';
            incorrects[i].disabled = true;
            corrects[i].style.opacity = '100%';
            feeds[i].innerHTML = "<span style='color: green;'>Correct Answer!</span>";
        });
    }

    for (let i = 0; i < incorrects.length; i++) {
        incorrects[i].addEventListener('click', function () {
            incorrects[i].style.backgroundColor = '#FF0000';
            corrects[i].style.backgroundColor = '#00FF00';
            corrects[i].disabled = true;
            incorrects[i].style.opacity = '100%';
            feeds[i].innerHTML = "<span style='color: red;'>Incorrect Answer!</span>";
        });
    }
});