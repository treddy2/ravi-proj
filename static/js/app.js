// Selector for blocks
var firstBlock  = document.getElementById('innerUl')
var secondBlock = document.getElementById('innerUlRight')



// Called when click on left to right
$(document).on('click', '#ltr', function(){
    console.log("welcome");
    for(i=0;i<firstBlock.children.length;i++){
        if(firstBlock.children[i].classList == 'selected'){
            secondBlock.appendChild(firstBlock.children[i])
            $(secondBlock).children('li').removeClass('selected')
        }
    }
})


// Called when click on right to left
$(document).on('click', '#rtl', function(){
    for(i=0;i<secondBlock.children.length;i++){
        if(secondBlock.children[i].classList == 'selected'){
            firstBlock.appendChild(secondBlock.children[i])
            $(firstBlock).children('li').removeClass('selected')
        }
    }
})




