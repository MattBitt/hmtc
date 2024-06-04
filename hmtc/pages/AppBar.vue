<template></template>

<script>
export default {
  data: () => {
    return {
      showNav: false,
      showApps: false,
      apps: [
        {
          title: "Home",
          icon: "fas fa-igloo fa-fw",
          colorTop: "#D1FE77",
          colorBottom: "#84B241",
        },
        {
          title: "Message",
          icon: "fas fa-comment-dots fa-fw",
          colorTop: "#FEFB81",
          colorBottom: "#E5AD4C",
        },
        {
          title: "Contact",
          icon: "fas fa-envelope fa-fw",
          colorTop: "#DEB59A",
          colorBottom: "#A78772",
        },
        {
          title: "Search",
          icon: "fas fa-search fa-fw",
          colorTop: "#B5BEFF",
          colorBottom: "#99A0E4",
        },
        {
          title: "Downloads",
          icon: "fas fa-cloud-download-alt fa-fw",
          colorTop: "#FD5D64",
          colorBottom: "#FF494E",
        },
        {
          title: "Gallery",
          icon: "fas fa-image fa-fw",
          colorTop: "#A7A8AB",
          colorBottom: "#8C8E91",
        },
        {
          title: "About",
          icon: "fas fa-user fa-fw",
          colorTop: "#83E9FE",
          colorBottom: "#71C7FA",
        },
        {
          title: "Calendar",
          icon: "fas fa-calendar-alt fa-fw",
          colorTop: "#84F9B2",
          colorBottom: "#6CCC91",
        },
        {
          title: "Youtube",
          icon: "fab fa-youtube fa-fw",
          colorTop: "#FD5D64",
          colorBottom: "#FF494E",
        },
        {
          title: "Twitter",
          icon: "fab fa-twitter fa-fw",
          colorTop: "#83E9FE",
          colorBottom: "#71C7FA",
        },
        {
          title: "Instagram",
          icon: "fab fa-instagram fa-fw",
          colorTop: "#B5BEFF",
          colorBottom: "#99A0E4",
        },
        {
          title: "Pinterest",
          icon: "fab fa-pinterest fa-fw",
          colorTop: "#FD5D64",
          colorBottom: "#FF494E",
        },
      ],
    };
  },
  methods: {
    showNavbar() {
      this.showNav = !this.showNav;
      setTimeout(() => {
        this.showApps = true;
      }, 600);
    },
  },
  computed: {
    getApps() {
      return this.showApps === true ? this.apps : [];
    },
  },
};
</script>

<style lang="scss" scoped>
.hdr {
  background: url("../assets/images/app_bg_z.jpg");
  background-attachment: fixed;
  background-size: cover;
  width: 100%;
  min-height: 100vh;
  overflow: hidden;
  transition: all 480ms;

  .nav-hamburger {
    padding: 20px;
    text-align: right;
    z-index: 9999;
    position: absolute;
    top: 0;
    right: 0;
    cursor: pointer;

    i {
      color: #fff;
      font-size: 2rem;
      cursor: pointer;
    }

    .container-burger {
      width: 4rem;
      height: 1.2rem;
      position: relative;
      cursor: pointer;

      &:hover {
        .line {
          background-color: #f71a01;

          &:nth-child(1) {
            width: 2.5rem;
          }

          &:nth-child(2) {
            width: 100%;
          }
        }
      }

      .line {
        width: 100%;
        height: 3px;
        background-color: #fff;
        position: absolute;
        display: block;
        right: 0;
        transition: all 0.3s;

        &:nth-child(1) {
          top: 0;
        }
        &:nth-child(2) {
          bottom: 0;
          margin-top: -1px;
          width: 2.5rem;
        }
      }
    }
  }

  .nav-container {
    //position: absolute;
    width: 100%;
    min-height: 100vh;
    overflow: hidden;
    display: flex;
    justify-content: center;
    align-items: center;
    top: 0;
    z-index: 1;
    backdrop-filter: blur(14px);
    position: fixed;
    right: 0;
    bottom: 0;

    &::before {
      content: "";
      position: absolute;
      width: 100%;
      min-height: 100%;
      background: inherit;
      box-shadow: inset 0 0 0 1000px rgba(0, 0, 0, 0.5);
      filter: blur(10px);
      z-index: 10;
    }

    .app-wrapper {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
      //width: 100%;
      min-width: 720px;

      .app-container {
        display: flex;
        justify-content: center;
        align-content: center;
        flex-direction: column;
        padding: 20px;
        z-index: 11;

        .app-card {
          display: flex;
          justify-content: center;
          align-items: center;
          width: 80px;
          height: 80px;
          border-radius: 50px;
          font-size: 2rem;
          cursor: pointer;
          transition: transform 0.2s ease-in-out;

          i {
            color: #fff;
          }

          &:hover {
            transform: scale(1.1);
          }
        }

        .app-title {
          color: #fff;
          font-size: 1.2rem;
          padding-top: 10px;
        }
      }
    }
  }

  .fade-enter-active,
  .fade {
    transition: all 0.8s ease;
  }
  .fade-enter-active,
  .fade-leave-active {
    transition: all 0.8s cubic-bezier(1, 0.5, 0.8, 1);
  }
  .fade-enter,
  .fade-leave-to {
    transform: translateX(100px);
    opacity: 0;
  }

  .slide-in-enter-active,
  .slide-in-leave-active {
    transition: opacity 0.5s linear,
      transform 0.5s cubic-bezier(0.23, 1, 0.32, 1);
    transition-delay: calc(0.1s * var(--i));
  }

  .slide-in-enter,
  .slide-in-leave-to {
    opacity: 0;
    transform: translateX(-1em);
  }
}
</style>
