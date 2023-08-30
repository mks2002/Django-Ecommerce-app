$("#slider1, #slider2, #slider3, #slider4, #slider5").owlCarousel({
  loop: true,
  margin: 20,
  responsiveClass: true,
  responsive: {
    0: {
      items: 1,
      nav: false,
      autoplay: true,
    },
    600: {
      items: 3,
      nav: true,
      autoplay: true,
    },
    1000: {
      items: 5,
      nav: true,
      loop: true,
      autoplay: true,
    },
  },
});

$(".plus-cart").click(function () {
  var id = $(this).attr("pid").toString();
  var eml = this.parentNode.children[2];
  console.log(id);
  $.ajax({
    type: "GET",
    url: "/pluscart",
    data: {
      prod_id: id,
    },
    success: function (data) {
      console.log(data);
      eml.innerText = data.quantity;
      document.getElementById("amount").innerText = data.amount.toFixed(2);
      document.getElementById("prodcnt").innerText = data.prodcnt;
      document.getElementById("totalamount").innerText =
        data.totalamount.toFixed(2);
    },
  });
});

$(".minus-cart").click(function () {
  var id = $(this).attr("pid").toString();
  var eml = this.parentNode.children[2];
  $.ajax({
    type: "GET",
    url: "/minuscart",
    data: {
      prod_id: id,
    },
    success: function (data) {
      console.log(data);
      eml.innerText = data.quantity;
      document.getElementById("amount").innerText = data.amount.toFixed(2);
      document.getElementById("prodcnt").innerText = data.prodcnt;
      document.getElementById("totalamount").innerText =
        data.totalamount.toFixed(2);
    },
  });
});

$(".remove-cart").click(function () {
  var id = $(this).attr("pid").toString();
  var elm = this;
  $.ajax({
    type: "GET",
    url: "/removecart",
    data: {
      prod_id: id,
    },
    success: function (data) {
      console.log(data);
      document.getElementById("amount").innerText = data.amount.toFixed(2);
      document.getElementById("prodcnt").innerText = data.prodcnt.toFixed(0);
      document.getElementById("totalamount").innerText = data.totalamount.toFixed(2);
      var msgelem = document.getElementById("msgbox");
      // always after removing a product change the number of cart objects in the navbar ..
      var navbarcnt =  document.getElementById("navcnt")
      navbarcnt.innerText = data.prodcnt.toFixed(0);
      msgelem.innerText = data.msg;
      msgelem.parentElement.classList.remove("alert-success");
      msgelem.parentElement.classList.add("alert-warning");
      elm.parentNode.parentNode.parentNode.parentNode.remove();

      // if totalamount is 0 then make payment button disabled ...
      var paymentButton = document.getElementById("paymentbtn");
      if (data.totalamount === 0) {
        paymentButton.classList.add("disabled");
        paymentButton.removeAttribute("href");
        paymentButton.style.pointerEvents = "none";
       

        // for the messagebox ...
        msgelem.parentElement.classList.remove("alert-warning");
        msgelem.parentElement.classList.add("alert-info");
      } else {
        paymentButton.classList.remove("disabled");
        paymentButton.href = "/checkout/?page=Cardpage";
        paymentButton.style.pointerEvents = "auto";
      }
    },
  });
});
