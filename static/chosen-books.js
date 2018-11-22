"use strict";

function initCollectBooksFormHandler() {
    $('#results-from-search').on('submit', evt => {
        evt.preventDefault();
        // pointers from https://stackoverflow.com/questions/5450104/using-jquery-to-get-all-checked-checkboxes-with-a-certain-class-name/14262603
        let checkedBooks = [];
        $('.bookCheckbox:checkbox:checked').map(function () {
            checkedBooks.push($(this).val());
            console.log(checkedBooks);
        });
        console.log(checkedBooks);
        for (let book of checkedBooks) {
            console.log(book);
            $.get('/search-by-book-id.json', {"book_id" : book}, (results) => {
                console.log(results);
                console.log(results.title);
                let li = $('<li><input type="checkbox" class="bookCheckbox" name="'+ results.title + '" value="' + results.book_id + '"/>' + '<label for="' + results.book_id + '"></label></li>');
                li.find('label').text(results.title);
                $('#chosenbklist').append(li);


    });
}
});
}

initCollectBooksFormHandler();