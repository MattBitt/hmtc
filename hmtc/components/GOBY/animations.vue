<template>
  <div>
    <h1>
      <a href="https://ashprincesskawaii.blogspot.co.id/"
        >Ash Princess Kawaii</a
      >
    </h1>
    <h2>HTML Marquee Tag</h2>
    <marquee
      class="html-marquee"
      direction="left"
      behavior="scroll"
      scrollamount="12"
    >
      <p>
        GUYS...ADA JAVASCRIPT YG GA BERFUNGSI DI 'WIDGET CUTE" KRN HOSTINGANNYA
        EXPIRED
      </p>
    </marquee>
    <div class="bounce">
      <p>BOUNCING TEXT</p>
    </div>
    <div class="marquee">
      <p>SCROLLING TEXT</p>
    </div>
    <div class="marquee-outer">
      <div class="marquee-inner">
        <img
          src="https://media.tumblr.com/d8ec7cd2939ded874728b30d46352ce9/tumblr_inline_mueo3z0asZ1qdlkyg.gif"
          width="94"
          height="88"
        />
      </div>
    </div>
    <v-col cols="12">
      <marquee behavior="slide" direction="up">Scrolling text...</marquee>
    </v-col>
  </div>
</template>
<style>
body {
  position: relative;
  margin: 10px;
  padding: 10px;
  background: url(https://3.bp.blogspot.com/-e7RZaDl68Gw/ToFyangs_EI/AAAAAAAAAxQ/nYAi2RJhJas/s000/botmen2.png)
    repeat;
  font-family: "arial";
  font-size: 16px;
  line-height: 1;
}
a:link,
a:visited {
  color: #e50099;
  cursor: url(http://media.tumblr.com/tumblr_lpyq1zoQPK1qcn2vb.gif),
    url(http://media.tumblr.com/tumblr_lpyq1zoQPK1qcn2vb.gif), auto;
  text-decoration: none;
}

a:hover {
  text-decoration: none;
  cursor: url(http://static.tumblr.com/xjqjg7j/BPsmxtr7z/10.gif),
    url(http://static.tumblr.com/xjqjg7j/BPsmxtr7z/10.gif), auto;
}
h1 {
  font-size: 28px;
  color: #e50099;
  text-transform: uppercase;
  text-align: center;
}
h2 {
  font-size: 18px;
  color: #c6eb04;
  text-align: center;
  text-transform: uppercase;
  text-shadow: 0 0 10px #c6eb04;
}
h3 {
  font-size: 11px;
  color: #f5a9e1;
}
.bounce {
  height: 50px;
  overflow: hidden;
  position: relative;
  font-weight: bold;
  background: #f3f781;
  color: #000;
  border: 1px solid #ccc;
}
.bounce p {
  position: absolute;
  width: 100%;
  height: 100%;
  margin: 0;
  line-height: 50px;
  text-align: center;
  /* Starting position */
  -moz-transform: translateX(50%);
  -webkit-transform: translateX(50%);
  transform: translateX(50%);
  /* Apply animation to this element */
  -moz-animation: bouncing-text 5s linear infinite alternate;
  -webkit-animation: bouncing-text 5s linear infinite alternate;
  animation: bouncing-text 5s linear infinite alternate;
}
/* Move it (define the animation) */
@-moz-keyframes bouncing-text {
  0% {
    -moz-transform: translateX(50%);
  }
  100% {
    -moz-transform: translateX(-50%);
  }
}
@-webkit-keyframes bouncing-text {
  0% {
    -webkit-transform: translateX(50%);
  }
  100% {
    -webkit-transform: translateX(-50%);
  }
}
@keyframes bouncing-text {
  0% {
    -moz-transform: translateX(50%); /* Browser bug fix */
    -webkit-transform: translateX(50%); /* Browser bug fix */
    transform: translateX(50%);
  }
  100% {
    -moz-transform: translateX(-50%); /* Browser bug fix */
    -webkit-transform: translateX(-50%); /* Browser bug fix */
    transform: translateX(-50%);
  }
}

.marquee {
  height: 50px;
  overflow: hidden;
  position: relative;
  background: #f5d0a9;
  color: #000;
  font-weight: bold;
  font-size: 16px;
  border: 1px solid #ccc;
}
.marquee p {
  position: absolute;
  width: 100%;
  height: 100%;
  margin: 0;
  line-height: 50px;
  text-align: center;
  /* Starting position */
  -moz-transform: translateX(100%);
  -webkit-transform: translateX(100%);
  transform: translateX(100%);
  /* Apply animation to this element */
  -moz-animation: scroll-left 5s linear infinite;
  -webkit-animation: scroll-left 5s linear infinite;
  animation: scroll-left 5s linear infinite;
}
/* Move it (define the animation) */
@-moz-keyframes scroll-left {
  0% {
    -moz-transform: translateX(100%);
  }
  100% {
    -moz-transform: translateX(-100%);
  }
}
@-webkit-keyframes scroll-left {
  0% {
    -webkit-transform: translateX(100%);
  }
  100% {
    -webkit-transform: translateX(-100%);
  }
}
@keyframes scroll-left {
  0% {
    -moz-transform: translateX(100%); /* Browser bug fix */
    -webkit-transform: translateX(100%); /* Browser bug fix */
    transform: translateX(100%);
  }
  100% {
    -moz-transform: translateX(-100%); /* Browser bug fix */
    -webkit-transform: translateX(-100%); /* Browser bug fix */
    transform: translateX(-100%);
  }
}

.marquee-outer {
  height: 100px;
  overflow: hidden;
  position: relative;
  color: #ffffff;
  background: #d0f5a9;
}
.marquee-inner {
  position: absolute;
  width: 100%;
  height: 100%;
  margin: 0;
  line-height: 50px;
  text-align: center;
  /* Starting position */
  -moz-transform: translateX(100%);
  -webkit-transform: translateX(100%);
  transform: translateX(100%);
  /* Apply animation to this element */
  -moz-animation: scroll-left 5s linear infinite;
  -webkit-animation: scroll-left 5s linear infinite;
  animation: scroll-left 5s linear infinite;
}
/* Move it (define the animation) */
@-moz-keyframes scroll-left {
  0% {
    -moz-transform: translateX(100%);
  }
  100% {
    -moz-transform: translateX(-100%);
  }
}
@-webkit-keyframes scroll-left {
  0% {
    -webkit-transform: translateX(100%);
  }
  100% {
    -webkit-transform: translateX(-100%);
  }
}
@keyframes scroll-left {
  0% {
    -moz-transform: translateX(100%); /* Browser bug fix */
    -webkit-transform: translateX(100%); /* Browser bug fix */
    transform: translateX(100%);
  }
  100% {
    -moz-transform: translateX(-100%); /* Browser bug fix */
    -webkit-transform: translateX(-100%); /* Browser bug fix */
    transform: translateX(-100%);
  }
}
.html-marquee {
  overflow: hidden;
  position: relative;
  background: #cef6f5;
  color: #000;
  font-weight: bold;
  font-size: 16px;
  border: 1px solid #ccc;
}
</style>
