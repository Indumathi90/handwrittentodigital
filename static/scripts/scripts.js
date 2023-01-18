$(document).ready(function() {
    $(".convert-button").click(function() {
      // disable button
      $(".convert-button").prop("disabled", true);
      // add spinner to button
      $(this).html(
        "Converting... <i class='fa fa-circle-o-notch fa-spin'></i> "
      );
      $(this).closest("form").submit()
    });
});