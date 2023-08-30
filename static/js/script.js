// $($.postRequest(apiURL, sendResponse))
/*==================== request sender wrapper ====================*/
openaiContent = [{ role: 'system', content: 'You are a summarizing bot' }]

userTemplate = "<div class='user'><div class='iconb'>User</div><div class='iconc'>$$contentReplace$$</div></div>"
botTemplate = "<div class='bot'><div class='iconc'>$$contentReplace$$</div><div class='iconb'>Bot</div></div>"

//placeholder template for table
tableTemplate = "<div id='tableresponse'>$$contentReplace$$</div>"

jQuery.extend({
  postRequest: function (url, params = {}) {
    let result = null;
    $.ajax({
      url: url,
      type: 'POST',
      data: params,
      //dataType: 'JSON',
      contentType: false,
      processData: false,
      async: false,
      ifModified: false,
      success: function (data, textstatus, xhr) {
        result = data;
      },
      error: function () {
        result = "null";
      }
    });
    return result;
  },
  getRequest: function (url) {
    let result = null;
    $.ajax({
      url: url,
      type: 'GET',
      dataType: 'JSON',
      async: false,
      ifModified: false,
      success: function (data, textstatus, xhr) {
        result = data;
      },
      error: function () {
        result = "null";
      }
    });
    return result;
  }
});

function bytesToSize(bytes) {
  var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  if (bytes == 0) return '0 Byte';
  var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
  return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
}

function validateSize(input) {
  const fileSize = input / 1024 / 1024; // in MiB
  if (fileSize > 2.5) {
    return false
  } else {
    return true
  }
}

function resetQuestion() {
  openaiContent = [{ role: 'system', content: 'You are a summarizing bot' }]
  return true
}

function botAction() {
  userQuestion = $("#userQuestion").val();
  document.getElementById('userQuestion').disabled = true;

  conte = userTemplate.replace("$$contentReplace$$", userQuestion)
  $("#botContents").append(conte)

  apiURL = "/botInfo"

  openaiContent.push({ 'role': 'user', 'content': userQuestion })

  var formData = new FormData();
  formData.append('questions', JSON.stringify(openaiContent));

  fetch(apiURL, {
    method: "post",
    body: formData
  })
    .then(response => response.json())
    .then((response) => {

      botResp = response?.answer || "Error in fetching"

      conte = botTemplate.replace("$$contentReplace$$", botResp.replace(/(?:\r\n|\r|\n)/g, '<br>'))
      $("#botContents").append(conte)

      var mydiv = $("#botContents");
      mydiv.scrollTop(mydiv.prop("scrollHeight"));

      $("#userQuestion").val("")

      document.getElementById('userQuestion').disabled = false;

    });



}

function contentProcess() {
  $("#rawcnt pre").text("")
  $("#table").html("")
  $("#proTable").html("")
  $("#opt-protable").addClass("hide")

  $('#sendProcess').prop("disabled", true);

  apiURL = "/predict"

  var formData = new FormData();
  // formData.append('contentType', $('#contentProcessType :selected').val());

  //if ($('#contentProcessType :selected').val() == "Arabic") {
  $("#opt-protable").removeClass("hide")
  //}

  formData.append('document', $('#uploadContent')[0].files[0]);

  fetch(apiURL, {
    method: "post",
    body: formData
  })
    .then(response => response.json())
    .then(response => {
      console.log(response)
      $("#processcnt").removeClass("hide")
      $("#pageloading").removeClass("pageloading")

      // resetQuestion()
      // data = response?.content
      // print(response)

      // conte = botTemplate.replace("$$contentReplace$$", JSON.stringify(response))

      // // create a table from the json response
      // table = createTable(response);
      // table.setAttribute("class", "tablecst")
      // table.setAttribute("id", "tablecont")
      // // get the bot contents elem and append the table to that
      // var botContents = document.getElementById("botContents")
      // botContents.appendChild(table)

      // // key = Object.keys(response)

      // // tablecnt = "<table class='tablecst'>"
      // // for (i = 0; i < key.length; i++) {
      // //   tablecnt += "<tr><td>" + key[i] + "</td><td>" + response[key[i]] + "</td></tr>"
      // // }
      // // tablecnt += "</table>"

      // // $("#botContents").html(tablecnt)

      

    });


}

// function to create a html table from json object
function createTable(data) {
  var table = document.createElement("table");
  table.classList.add("table");

  // directly create the table rows
  Object.keys(data).forEach(function (key) {
    var row = table.insertRow();
    var row_data = data[key];
    Object.keys(row_data).forEach(function (col_key) {
      if (key == '0'){
        var attributeCell = row.insertCell();
        attributeCell.textContent = col_key;
        var attribute
      }
      var attributeCell = row.insertCell();
      attributeCell.textContent = row_data[col_key];
    })
      
  })
  return table;
}

function deleteTable() {
  var table = document.getElementById("botContents");
  table.innerHTML = "";
}

$(document).ready(function () {

  $('#resetUpload').on('click', function (e) {
    deleteTable()

    $("#fileDetails").html("")

    $(".prevSh").addClass("hide")
    $('#uploadContent').val('');;
    $("#upload-cntr").removeClass("hide")

    $(".previewImg").addClass("hide")

    $("#fileType-chk").removeClass("successclr")
    $("#fileType-chk span").removeClass("fa-check-square")
    $("#fileType-chk").removeClass("failedclr")
    $("#fileType-chk span").removeClass("fa-minus-square")

    $("#fileSize-chk").removeClass("successclr")
    $("#fileSize-chk span").removeClass("fa-check-square")
    $("#fileSize-chk").removeClass("failedclr")
    $("#fileSize-chk span").removeClass("fa-minus-square")

    $(".jsGridView").addClass('hide')
    $("#introcnt").removeClass("hide")
    $('#sendProcess').prop("disabled", true);





  });

  $('#sendProcess').on('click', function (e) {
    $("#pageloading").addClass("pageloading");

    contentProcess()


  });

  $('#botAction').on('click', function (e) {

    if (!$("#userQuestion").is(":disabled"))
      botAction()
  });

  $('#userQuestion').keypress(function (e) {
    var key = e.which;
    if (key == 13)  // the enter key code
    {
      if (!$("#userQuestion").is(":disabled"))
        botAction()
      return false;
    }
  });

  $('#uploadContent').change(function (e) {
    currentfile = e.target.files[0]
    mimeType = currentfile.type

    imgContentPreview = $("#contentPreview.img")
    pdfContentPreview = $("#contentPreview.pdf")

    isImg = false
    isPdf = false

    successclr = "successclr"
    failedclr = "failedclr"

    successIcon = "fa-check-square"
    failedIcon = "fa-minus-square"

    currentType = mimeType.split('/')[0]
    currentOpts = mimeType.split('/')[1]

    fileDetails = "<div class='message-box' style='display: flex;width: 100%;'><span style='flex: 1;'>File Name</span><span style='flex: 2;'>" + currentfile.name + "</span></div>"
    fileDetails += "<div class='message-box' style='display: flex;width: 100%;'><span style='flex: 1;'>File Size</span><span style='flex: 2;'>" + bytesToSize(currentfile.size) + "</span></div>"
    fileDetails += "<div class='message-box' style='display: flex;width: 100%;'><span style='flex: 1;'>Mime Type</span><span style='flex: 2;'>" + currentfile.type + "</span></div>"

    if (currentType === 'image') {
      isImg = true
    }

    if (currentOpts === 'pdf') {
      isPdf = true
    }

    $(".prevSh").addClass("hide")

    if (isImg || isPdf) {

      if (isImg) {
        $(".previewImg").addClass("hide")
        imgContentPreview.attr("src", URL.createObjectURL(currentfile))
        $(".previewImg.img").removeClass("hide")
      } else {
        $(".previewImg").addClass("hide")
        pdfContentPreview.attr("src", URL.createObjectURL(currentfile))
        $(".previewImg.pdf").removeClass("hide")
      }

      //$(".previewImg").addClass("hide")
      //pdfContentPreview.attr("src", URL.createObjectURL(currentfile))
      //$(".previewImg.pdf").removeClass("hide")

      $("#preview-cntr").removeClass("hide")
      $("#fileType-chk").addClass(successclr)
      $("#fileType-chk span").addClass(successIcon)

      $('#sendProcess').prop("disabled", false);
    } else {
      $("#fileType-chk").addClass(failedclr)
      $("#fileType-chk span").addClass(failedIcon)

      $('#sendProcess').prop("disabled", true);
    }

    if (validateSize(currentfile.size)) {
      $("#fileSize-chk").addClass(successclr)
      $("#fileSize-chk span").addClass(successIcon)

      $('#sendProcess').prop("disabled", false);
    } else {
      $("#fileSize-chk").addClass(failedclr)
      $("#fileSize-chk span").addClass(failedIcon)

      $('#sendProcess').prop("disabled", true);
    }

    $("#fileDetails").html(fileDetails)

  });

});