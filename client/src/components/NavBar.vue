<template>
  <nav>
    <div class="logo">
      <img class="image" src="@/assets/images/logo.png" alt="managr logo" />
      <span class="name">
        managr
      </span>
    </div>
    <div class="links">
      <NavLink icon="leads" :active="this.$route.path === '/leads'">Leads</NavLink>
      <NavLink icon="prospect">Prospect</NavLink>
      <NavLink icon="forecast">Forecast</NavLink>
      <NavLink icon="reports">Reports</NavLink>
    </div>
    <img
      src="@/assets/images/screenshots/navbar-search-and-profile.png"
      alt="screenshot"
      class="navbar-search-and-profile"
    />
  </nav>
</template>

<script>
import NavLink from '@/components/NavLink'

export default {
  name: 'NavBar',
  components: {
    NavLink,
  },
}
</script>

<style lang="scss" scoped>
@import url('https://fonts.googleapis.com/css2?family=Quicksand&display=swap');

nav {
  display: flex;
  align-items: center;
  background-color: #ffffff;
}

.logo {
  margin-left: 35px;
  display: flex;
  align-items: center;

  .image {
    width: 40px;
    height: 40px;
  }

  .name {
    width: 111px;
    height: 35px;
    font-family: Quicksand;
    font-size: 24px;
    font-weight: 500;
    font-stretch: normal;
    font-style: normal;
    line-height: normal;
    color: #199e54;
  }
}

.links {
  display: flex;
  flex-flow: row;
  margin-left: 26%;
  width: 28%;
}

.navbar-search-and-profile {
  height: 34px;
  margin-left: auto;
  margin-right: 34px;
}
</style>
