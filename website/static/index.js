function loadMore(){
    fetch('/loadmore',{
        method:'POST'}).then((_res)=>{
        window.location.href = "/";
    })
}
