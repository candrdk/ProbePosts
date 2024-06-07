let page_num = 0;

// If we receive nothing, set page_num to -1 to indicate that
// no more pages can be fetched.
function addPosts() {
    if (page_num < 0) { return; }

    let loc = window.location.href;
    if (loc.lastIndexOf('?') == -1) loc = loc+'/page/'+page_num;
    else loc = loc.replaceAll(/\?/g, '/page/'+page_num+'?'); 

    $.get(loc, function(data) {
        if (data) { 
            $('#page_end_marker').before(data);
        }
        else {
            page_num = -1;
        }
    });

    page_num += 1;
}

const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            addPosts();
        }
    });
});

io.observe(document.getElementById("page_end_marker"));

addPosts();
