function restore(){
  $("#record, #live").removeClass("disabled");
  $(".one").addClass("disabled");
  Fr.voice.stop();
}
$(document).ready(function(){
  $(document).on("click", "#record:not(.disabled)", function(){
    elem = $(this);
    Fr.voice.record($("#live").is(":checked"), function(){
      elem.addClass("disabled");
      $("#live").addClass("disabled");
      $(".one").removeClass("disabled");
    });
  });
  
  $(document).on("click", "#stop:not(.disabled)", function(){
    Fr.voice.export(function(url){
      $("#audio").attr("src", url);
    }, "URL");
    restore();
  });
  
  $(document).on("click", "#download:not(.disabled)", function(){
    Fr.voice.export(function(url){
      console.log("<a href='"+url+"' download='MyRecording.wav'></a>");
      $("<a href='"+url+"' download='MyRecording.wav'></a>")[0].click();
    }, "URL");
    restore();
  });
});
