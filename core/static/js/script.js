let but=document.querySelector('.bar')
but.addEventListener('click',()=>{
let s=document.querySelector('.nav-links')
if (s.style.display==="flex"){
    s.style.display="none"
}else{
    s.style.display="flex"
}
});


window.addEventListener('resize',
    function(){
        let s=this.document.querySelector('.nav-links2')
        if(window.innerWidth>500){
            s.style.display='none'
        }
  
    }
);

document.getElementById("downloadCsvBtn").addEventListener("click", function () {
    window.open("{% url 'export' %}", '_blank');
});