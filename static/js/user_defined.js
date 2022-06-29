function ddlselect()
{
  var d = document.getElementById("techweight");
  var displaytext=d.options[d.selectedIndex].text;
  document.getElementById("tierweight").value=100-displaytext;
}




 var form = $("#my-form1");
  $("#rsubmit").on("click",function() {
    $.ajax({
        type: form.attr("method"),
        url: form.attr("action"),
        data: form.serialize(),
        beforeSend: function(){
        $("#loader").show();
        },
        complete: function(){
        $("#loader").hide();
        },
        success: function(){
        var output = '<div class="row"><div class="column"><h5><b><p style="color:#F75D59">Please wait a moment.</p></b></h5></div><div class="column"><img src="/static/img/ajax-loader-lines.gif"></div></div>';
        $("#result").html(output);
        },
        error: function(){
        var output1 = '<h5><b><p style="color:red">Error in fetching data.</p></b></h5>';
        $("#result").html(output1);
        }
    });
  });
    $('#dtHorizontalVerticalExample').DataTable({
    "scrollX": true,
    "scrollY": 200,
    });
    $('.dataTables_length').addClass('bs-select');

  $("#fileNames").change(function() {
    var relPath = "/Resumes/"
    var sourceVal = document.getElementById("fileNames").files[0].webkitRelativePath;
    var sourceDirectry = sourceVal.substr(0, sourceVal.lastIndexOf("/"))
    var pathDirectory = relPath.concat(sourceDirectry);
    $("#sourceDirPath").val(pathDirectory);
  });

    $('#my_modal23').on('show.bs.modal', function(e) {
  var skillsId23 = $(e.relatedTarget).data('book-id');
  $(e.currentTarget).find('textarea[name="skillsId23"]').val(skillsId23);
});
});


$("#submit").click(function(){
  var text = $("#textarea").val();
  $("#modal_body").html(text);
});


