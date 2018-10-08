$(document).ready(function() {

    // setting all variables.

    var canvas = $('canvas')[0]; // canvas
    var ctx = canvas.getContext("2d"); // context
    
    // width , height
    var width = canvas.width;
    var height = canvas.height;
    
    
    var board = [   0, 0, 0,
                    0, 0, 0,
                    0, 0, 0 ]; // board
    // -1 is Human 
    //  1 is AI 
    //  0 is empty
    


    var human_btn = $("#human_btn"); // I'll go first button
    var ai_btn = $("#ai_btn"); // You go first button
    
    var human_art_isX = null;
    var isHumanTurn = false;
    var options = $(".options");


    var status = $("#status");

    // game status
    var gameRunning = false;

    // hide options funciton 
    function hideOptions(doHide = true) {
        if(doHide) {
            options.hide();
        } else {
            options.show();
        }
    }


    // clear Board
    function clearBoard() {
        ctx.clearRect(0, 0, width, height);
    }

    // draw Board
    function drawBoard() {
        ctx.beginPath();
        ctx.moveTo(100,0);
        ctx.lineTo(100,300);
        ctx.moveTo(200,0);
        ctx.lineTo(200,300);
        ctx.moveTo(0,100);
        ctx.lineTo(300,100);
        ctx.moveTo(0,200);
        ctx.lineTo(300,200);
        ctx.stroke();
    }

    // reset board
    function resetBoard() {
        board = [   0, 0, 0,
                    0, 0, 0,
                    0, 0, 0 ];
    }

    // start Game
    function startGame() {
        resetBoard();
        hideOptions(true);
        drawBoard();
    }

    

    // mouse event handelrs
    $(canvas).on('mousedown', function(evt) {
        if(!gameRunning || !isHumanTurn) return;
        isHumanTurn = false;
        var rect = canvas.getBoundingClientRect();
        var xpos = Math.floor((evt.clientX - rect.left) / (width/3)) ;
        var ypos = Math.floor((evt.clientY - rect.top) / (height/3));
        var completed = drawHumanAt(xpos,ypos);
        // after Human has played
        if(completed) {
            MachinePlay();
        } else {
            isHumanTurn = true
        }
    });


    // 
    function checkRoutineGameStatus() {

        // check if all are filled
        var humanWon = false;
        var AIWon = false;
        isVacent = false;
        for(var i=0;i<board.length;i++) {
            if(board[i] == 0) {
                isVacent = true;
            }
        }

        // check for rows
        for(var i=0;i<board.length;i+=3) {
            var rowsum = board[i] + board[i+1] + board[i+2];
            if(rowsum == 3) {
                AIWon = true;
            } else if(rowsum == -3) {
                humanWon = true;
            }
        }

        // check cols
        for(var i=0;i<3;i++) {
            var colsum = board[i] + board[i+3] + board[i+6];
            if(colsum == 3) {
                AIWon = true;
            } else if(colsum == -3) {
                humanWon = true;
            }
        }

        // check digonals
        var sum_ld = board[0] + board[4] + board[8]
         if(sum_ld == 3) {
            AIWon = true;
        } else if(sum_ld == -3) {
            humanWon = true;
        }

        var sum_rd = board[2] + board[4] + board[6]
        if(sum_rd == 3) {
            AIWon = true;
        } else if(sum_rd == -3) {
            humanWon = true;
        }

        if(AIWon) {
            status.text("Matias venceu!! O que houve? Não consegue vencer a IA?");
            gameRunning = false;
            hideOptions(false);
            return false;
        } else if(humanWon) {
            status.text("Você venceu!!!, Você é mais inteligente que a IA! Ufa!");
            gameRunning = false;
            hideOptions(false);
            return false;
        } else if(!isVacent) {
            status.text("Empate!!");
            gameRunning = false;
            hideOptions(false);
            return false;
        } else {
            return true;
        }

    } 

    // detla's
    var xdelta = 15 
    var ydelta = -15

    // drawHuman
    function drawHumanAt(xpos,ypos) {
        if(human_art_isX) {
            return drawAt('X',xpos,ypos,-1);
        } else {
            return drawAt('O',xpos,ypos,-1);
        }
    }

    // draw art at 
    function drawAt(character , xpos , ypos, player) {
        var index = xpos + ypos*3;
        if(board[index] == 0) {
            board[index] = player;
            ctx.font = "100px Arial";
            ctx.fillText(character, (xpos ) * (width / 3) + xdelta   , (ypos+1) * (height / 3   ) + ydelta );
        } else {
            return false;
        }
       // if(player == -1)
            //console.log("Human CLick ,  ",xpos,ypos,index,board);
      //  else 
            //console.log("Machine CLick ", xpos,ypos,index,board);
        return checkRoutineGameStatus();
    }

   

    // initialize the game
    function init() {
        clearBoard();
        drawBoard();
        hideOptions(false);
    }
    init();

    // 'you play first' button click
    human_btn.on('click',function(e) {
        var human_art = $('input[name=art]:checked').val();
        if(human_art == 'X')
            human_art_isX = true;
        else
            human_art_isX = false;
        
        hideOptions();
        clearBoard();
        resetBoard();
        drawBoard();
        isHumanTurn = true;
        gameRunning = true;
        status.text("")

    });


    // AI button on click
    ai_btn.on('click',function() {
        var human_art = $('input[name=art]:checked').val();
        if(human_art == 'X')
            human_art_isX = true;
        else
            human_art_isX = false;
        
        hideOptions();
        resetBoard();
        clearBoard();
        drawBoard();
        isHumanTurn = false;
        gameRunning = true;
        status.text("")
        MachinePlay();

    })


    // let the machine play
    function MachinePlay() {
        //console.log(JSON.stringify(board));
        $.ajax({
            type: 'POST',
            url: "/api/ticky",
            data: JSON.stringify({'data': board}),
            dataType: "json",
            contentType: "application/json",
            success: function(data) {
               // console.log("Machine suggests to play at ",data)
                xpos = data%3;
                ypos = Math.floor(data/3);
               // console.log("machine Play: " + data+" "+xpos+" "+ypos);
                if(human_art_isX) {
                     drawAt('O',xpos,ypos,1);
                } else {
                    drawAt('X',xpos,ypos,1);
                }
                isHumanTurn = true;
            }
        });    
    }

});