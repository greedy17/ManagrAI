<template>
  <div>
    <div class="sidenav sidenav__background">
      <div>
        <h2 class="title">Smart Alerts</h2>
      </div>
      <router-link exact-active-class="active" :to="{ name: 'CreateNew' }">
        <div class="row">
          <img
            src="@/assets/images/template.png"
            style="height: 1rem; margin-right: 0.5rem"
            alt=""
          />
          <h3>Templates</h3>
        </div>
      </router-link>

      <router-link exact-active-class="active" :to="{ name: 'BuildYourOwn' }">
        <div class="row">
          <img src="@/assets/images/build.png" style="height: 1rem; margin-right: 0.5rem" alt="" />
          <h3>Build your own</h3>
        </div>
      </router-link>

      <router-link exact-active-class="active" :to="{ name: 'ListTemplates' }">
        <div class="row">
          <img src="@/assets/images/edit.png" style="height: 1rem; margin-right: 0.5rem" alt="" />
          <h3>Run/Edit</h3>
        </div>
      </router-link>

      <div>
        <div class="row">
          <img
            src="@/assets/images/analyze.png"
            style="height: 1.25rem; margin-right: 0.5rem"
            alt=""
          />
          <h3>Analyze <span class="coming-soon">coming soon</span></h3>
        </div>
      </div>
    </div>

    <div v-if="isHome" style="margin-left: 6vw">
      <h2 style="color: white">Smart Alerts</h2>
      <p style="font-weight: bold; color: #beb5cc; margin-top: -0.5rem">
        Automated workflows that keep you on track
      </p>
    </div>

    <router-view :key="$route.fullPath"></router-view>
  </div>
</template>

<script>
export default {
  name: 'AlertsDashboardMenu',
  computed: {
    isHome() {
      return this.$route.name == 'alerts'
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.coming-soon {
  @include muted-font(13px);
}

.sidenav {
  height: 100%;
  width: 15vw;
  position: fixed;
  z-index: 1;
  left: 0;
  background-color: $panther;
  border: 2px solid $panther-silver;
  border-radius: 0.25rem;
  color: $panther-silver;
  overflow-x: hidden;
  padding-top: 20px;
  padding: 1rem;
}
a {
  text-decoration: none;
  font-weight: bold;
  color: $panther-silver;
  cursor: pointer;
}
a:hover {
  color: white;
  cursor: pointer;
}
.active {
  color: white;
  text-shadow: 0 0 20px $panther-gold;
}
.title {
  color: $panther-orange;
  font-weight: bold;
}
.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}
</style>
