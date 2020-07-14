<template>
  <div class="menu-item">
    <div @click="toggleParent" class="menu-item__main">
      <!-- Currently using a href, and router link, but will be changed to a router-link -->

      <span
        class="menu-item__title"
        :class="{
          primary: primary,
          selected: selectedItem == menuItems.name,
          expanded: expandParent,
        }"
        >{{ menuItems.name }}</span
      >

      <svg v-if="menuItems.options.length > 0" class="icon" fill="black" viewBox="0 0 30 30">
        <use xlink:href="~@../../../public/img/collection.svg#caret-down" />
      </svg>
    </div>

    <template v-if="expandParent">
      <div class="menu-item__sub" :key="o" v-for="(i, o) in menuItems.options">
        <expandable-menu-items
          :primary="!!i.primary"
          :menuItems="i"
          :defaultExpanded="i.expanded"
        />
      </div>
    </template>
  </div>
</template>
<script>
export default {
  name: 'ExpandableMenu',
  props: {
    menuItems: {
      type: Array,
    },
    primary: {
      default: false,
      type: Boolean,
    },
    defaultExpanded: {
      default: false,
      type: Boolean,
    },
  },
  data() {
    return {
      expandParent: '',
      selected: false,
    }
  },
  computed(){
      selectedItem(){},
      currentRoute(){},

  },
  methods:{
      toggleParent(){
          this.expandParent=!this.expandParent
          this.setSelected(this.menuItems)
      },
      setSelected(val){
          return
      }
  }
}
</script>
<style scoped lang="scss">
.menu-item {
  display: flex;
  flex-direction: column;
  align-items: left;
  &__main {
    display: flex;
    // show the items in the main class, reverse the row and set them to the end
    // doing this will give us css ~ sibling accessor to rotate the arrow
    flex-direction: row-reverse;
    align-items: center;
    justify-content: flex-end;
    > * {
      cursor: pointer;
    }
    &:hover {
      background-color: lightcyan;
    }
  }
  &__title {
    // if it is the title of a menu item capitalize it
    color: black !important;
    font: normal 16px/30px Roboto;
    text-transform: capitalize;
    cursor: pointer;
  }
  &__title.primary {
    // if it is primary then make it uppercase and bold
    font-weight: bold;
    color: gray !important;
    text-transform: uppercase;
  }
  &__title.selected {
    // if it is selected make it bold
    font-weight: bold;
  }
  &__title.expanded ~ .icon {
    // if expanded and has an expandable icon, rotate
    transform: rotate(0deg);
  }

  &__title.nav-link {
    font-weight: normal;
    border: none;
    color: black !important;
  }
  &__title.nav-link.router-link-exact-active {
    font-weight: bold;
  }
  &__title.nav-link.selected {
    font-weight: bold;
  }

  &__sub {
    // for each nest push out by 1 rem
    color: black;
    margin-left: 1rem;
  }
  &__sub.selected {
    font-weight: bold;
  }
}
.icon {
  // start caret-down rotated and all expanded
  display: block;
  cursor: pointer;
  width: 10px;
  height: 10px;
  margin-right: 0.5rem;
  transform: rotate(-90deg);
}
</style>
