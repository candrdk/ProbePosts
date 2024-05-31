
const count = 10;
let page_num = 0;

function addPosts() {
    $.get(window.location.href + '/page/' + page_num, function(data) {
        $('#page_end_marker').before(data);
    });
    
    page_num += 1;
}

const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            addPosts();
        }
    });
});

io.observe(document.getElementById("page_end_marker"));

addPosts();
