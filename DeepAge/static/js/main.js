function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $('#placeholderimg').attr('src', e.target.result);
        }

        reader.readAsDataURL(input.files[0]);
    }
}
//Randomly Shuffle an input array
function shuffleArray(array) {
    for (var i = array.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
    return array;
}
$("#imgInp").change(function(){
    readURL(this);
});
$(document).on("click","#uploadbtn",function(){
    var file_data=$('#imgInp').prop("files")[0];//Retrieve the image uploaded by the user
    var form_data=new FormData();//Create a form object to be sent as a post request
    form_data.append("file",file_data);
    $.ajax({
        url:"/getAge/",
        contentType: false,
        processData: false,
        dataType:"json",
        data: form_data,                         // Setting the data attribute of ajax with file_data
        type: 'post',
    }).done(function(data){
        if(data["success"]!=undefined && data["success"]==true){
            $('#placeholderimg').attr('src',"data:image/jpeg;base64," +data["img"]);//Place the image marked with faces in place of the original image
            $('#placeholderimg').width(256).height(256);//Reduce the size of the image
            if($('#faceresult').length<=0){//If the result block is not already present, create a new one
                $('#placeholder').addClass('resultblock');
                $("<div id='faceresult' class='resultblock'></div>").insertAfter('#placeholder');
            }
            $('#faceresult').empty();//Remove all the existing contents of the result block
            facedata=data["faces"];//Storing all the facial data
            var NUM_FACES=data["num_faces"];
            if(NUM_FACES>30){//Maximum number of faces displayed in the interface is 30
                //facedata=shuffleArray(facedata).slice(0,30);
                NUM_FACES=30;
            }
            var NUM_COL_ELEMENTS=10;
            if(NUM_FACES<10){
                NUM_COL_ELEMENTS=NUM_FACES;
            }
            var NUM_COL=Math.ceil(NUM_FACES *1.0/10);
            var AGE_COL_WIDTH=100.0/(3*NUM_COL);
            $('#faceresult').append(
                '<table class="table-bordered" id="resultstable">'+
                '<thead><tr></tr></thead>'+
                '<tbody></tbody>'+
                '</table>'
            );
            for(var i=0;i<NUM_COL;i++){
                $('#resultstable thead tr').append(
                    '<th>Face</th>'+
                    '<th>Age Group</th>'
                );
            }
            for(var i=0;i<NUM_FACES;i+=NUM_COL){
                $('#resultstable tbody').append(
                    '<tr>'+
                    '</tr>'
                );
                var lastrow=$('#resultstable tbody tr:last-child');
                for(var j=i;j<i+NUM_COL;j++){
                    if(j>=NUM_FACES){
                        break;
                    }
                    var face=facedata[j];
                    lastrow.append(
                        '<td class="facebox">'+
                        '<img class="faceimg" src="data:image/jpeg;base64,'+face["faceimg"]+'">'+
                        '</td>'
                    );
                    lastrow.append(
                        '<td class="agebox">'+
                        face["age"]+
                        '</td>'
                    );
                }
            }

            $('.faceimg').css({
                'max-height': 100.0/(NUM_COL_ELEMENTS+2)+'%',
                'height': 100.0/(NUM_COL_ELEMENTS+2)+'%'
            });

            $('#resultstable thead tr th:nth-child(even)').css({
                'width': AGE_COL_WIDTH+"%"
            });
        }
    })
})