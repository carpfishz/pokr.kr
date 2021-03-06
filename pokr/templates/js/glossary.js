(function () {
var dictionary = {{ dictionary|safe }};
$(function () {
    $('.glossary').each(function () {
        var html = $(this).html();
        var annotated = html.replace(/{{ terms_regex|safe }}/g, function (term) {
            var meaning = dictionary[term];
            return '<span class="tooltipped annotated" data-placement="bottom" data-title="' + meaning + '">' + term + '</span>';
        });
        $(this).html(annotated);
    });
})
}());

