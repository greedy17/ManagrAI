<template>
  <div>
    <Modal v-if="deleteModelOpen" class="delete-modal">
      <div class="delete-container">
        <header @click="toggleDeleteModal">
          <p>X</p>
        </header>
        <main>
          <h2>Delete Search</h2>
          <p>Are you sure you want to delete this search ?</p>

          <div style="margin-top: 20px" class="row">
            <button @click="toggleDeleteModal" class="tertiary-button">Cancel</button>
            <button @click="deleteSearch" class="red-button">Delete</button>
          </div>
        </main>
      </div>
    </Modal>
    <Transition name="slide-fade">
      <div v-if="showUpdateBanner" class="templates">
        <p>Search successfully deleted!</p>
      </div>
    </Transition>
    <div v-if="userIsLoggedIn">
      <nav id="nav" v-if="isPR">
        <router-link :to="{ name: 'PRSummaries' }">
          <div @click="goHome" class="logo">
            <img style="height: 28px" src="@/assets/images/logo.png" />
            <div class="beta-tag">
              <p>BETA</p>
            </div>
          </div>
        </router-link>

        <router-link active-class="active" :to="{ name: 'PRSummaries' }">
          <p>Digest</p>
        </router-link>

        <router-link active-class="active" :to="{ name: 'Pitches' }">
          <p>Pitch</p>
        </router-link>

        <router-link v-if="!hasZoomIntegration" :to="{ name: 'PRIntegrations' }">
          <!-- <p>Transcribe</p> -->
          <div class="wrapper">
            <p>Transcribe</p>
            <div style="margin-left: -20px" class="tooltip">Connect Zoom</div>
          </div>
        </router-link>

        <router-link v-else active-class="active" :to="{ name: 'PRTranscripts' }">
          <p>Transcribe</p>
        </router-link>

        <!-- <a @mouseenter="textSoonOn" @mouseleave="textSoonOff">{{ soonText }}</a> -->

        <div class="auto-left">
          <!-- <div v-if="$route.name === 'PRSummaries' || $route.name === 'Pitches'" class="nav-text">
            <button @click="goHome" class="tertiary-button">
              {{
                $route.name === 'PRSummaries'
                  ? 'New Search'
                  : $route.name === 'Pitches'
                  ? 'New Pitch'
                  : ''
              }}
            </button>
          </div> -->

          <div class="relative">
            <div
              v-if="$route.name === 'PRSummaries'"
              @click="toggleShowSearches"
              class="row pointer nav-text"
            >
              Saved Searches
              <img
                v-if="!showSavedSearches"
                src="@/assets/images/downArrow.svg"
                height="14px"
                alt=""
              />
              <img
                class="rotate-img"
                v-else
                src="@/assets/images/downArrow.svg"
                height="14px"
                alt=""
              />
            </div>

            <div v-if="showSavedSearches" class="search-dropdown">
              <div class="input">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                  <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M4.1 11.06a6.95 6.95 0 1 1 13.9 0 6.95 6.95 0 0 1-13.9 0zm6.94-8.05a8.05 8.05 0 1 0 5.13 14.26l3.75 3.75a.56.56 0 1 0 .8-.79l-3.74-3.73A8.05 8.05 0 0 0 11.04 3v.01z"
                    fill="currentColor"
                  ></path>
                </svg>
                <input class="search-input" v-model="searchText" :placeholder="`Search...`" />
                <img
                  v-show="searchText"
                  @click="clearText"
                  src="@/assets/images/close.svg"
                  class="invert pointer"
                  height="12px"
                  alt=""
                />
              </div>
              <p class="v-margin" v-if="!searches.length">Nothing here...</p>

              <div class="searches-container">
                <div
                  @mouseenter="setIndex(i)"
                  @mouseLeave="removeIndex"
                  class="row relative"
                  v-for="(search, i) in searches"
                  :key="search.id"
                >
                  <img
                    class="search-icon invert"
                    v-if="search.type === 'NEWS'"
                    src="@/assets/images/memo.svg"
                    height="12px"
                    alt=""
                  />
                  <img
                    class="search-icon"
                    v-else-if="search.type === 'SOCIAL_MEDIA'"
                    src="@/assets/images/comment.svg"
                    height="12px"
                    alt=""
                  />
                  <p @click="selectSearch(search)">
                    {{ search.name }}
                  </p>

                  <img
                    @click="toggleDeleteModal(search)"
                    v-if="hoverIndex === i"
                    class="absolute-icon"
                    src="@/assets/images/trash.svg"
                    height="12px"
                    alt=""
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- <div class="row pointer">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-label="Lists">
              <path
                d="M6.44 6.69h0a1.5 1.5 0 0 1 1.06-.44h9c.4 0 .78.16 1.06.44l.35-.35-.35.35c.28.28.44.66.44 1.06v14l-5.7-4.4-.3-.23-.3.23-5.7 4.4v-14c0-.4.16-.78.44-1.06z"
                stroke="currentColor"
              ></path>
              <path
                d="M12.5 2.75h-8a2 2 0 0 0-2 2v11.5"
                stroke="currentColor"
                stroke-linecap="round"
              ></path>
            </svg>
          </div> -->

          <div class="row right-mar avatar-container">
            <div @click="toggleMenu" class="avatar">{{ getInitials() }}</div>
            <!-- <img
              @click="toggleMenu"
              v-if="!menuOpen"
              src="@/assets/images/rightarrow.svg"
              height="14px"
              alt=""
            />
            <img
              v-else
              @click="toggleMenu"
              class="pointer"
              src="@/assets/images/downArrow.svg"
              height="14px"
              alt=""
            /> -->

            <div v-if="menuOpen" class="avatar-dropdown">
              <p class="dropdown-item" @click="goToSettings">
                <!-- <img class="mar-right" src="@/assets/images/settings.svg" height="14px" alt="" /> -->
                <img class="mar-right" src="@/assets/images/profile.svg" height="14px" alt="" />
                Users
              </p>
              <p class="dropdown-item" @click="goToIntegrations">
                <img class="mar-right" src="@/assets/images/apps.svg" height="14px" alt="" />
                Integrations
              </p>
              <p @click="logOut" class="dropdown-item dropdown-border">
                <img class="mar-right" src="@/assets/images/logout.svg" height="14px" alt="" /> Sign
                out
              </p>
            </div>
          </div>
        </div>
      </nav>
    </div>
  </div>
</template>

<script>
import { CollectionManager } from '@thinknimble/tn-models'
import { Comms } from '@/services/comms'

export default {
  name: 'NavBar',
  components: {
    CollectionManager,
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
  },
  props: {
    menuOpen: { type: Boolean },
  },
  data() {
    return {
      items: [],
      searchText: '',
      showSavedSearches: false,
      deleteModelOpen: false,
      selectedSearch: null,
      soonText: 'Transcribe',
      hoverIndex: null,
      showUpdateBanner: false,
    }
  },
  created() {
    this.getSearches()
  },
  methods: {
    setIndex(i) {
      this.hoverIndex = i
    },
    removeIndex() {
      this.hoverIndex = null
    },
    textSoonOn() {
      this.soonText = 'Coming Soon!'
    },
    textSoonOff() {
      this.soonText = 'Transcribe'
    },
    toggleDeleteModal(search = null) {
      if (search) {
        this.selectedSearch = search
      }
      this.deleteModelOpen = !this.deleteModelOpen
      this.showSavedSearches = false
    },
    async deleteSearch() {
      try {
        await Comms.api
          .deleteSearch({
            id: this.selectedSearch.id,
          })
          .then(() => {
            this.$store.dispatch('getSearches')
            this.deleteModelOpen = false
            this.showUpdateBanner = true
          })
      } catch (e) {
        console.log('ERROR DELETING SEARCH', e)
      } finally {
        setTimeout(() => {
          this.showUpdateBanner = false
        }, 2000)
      }
    },
    getInitials() {
      const fullSplit = this.fullName.split(' ')
      let initials = ''
      fullSplit.forEach(word => initials += word[0])
      return initials
    },
    selectSearch(search) {
      this.toggleShowSearches()
      this.$store.dispatch('setSearch', search)
    },
    toggleShowSearches() {
      this.showSavedSearches = !this.showSavedSearches
    },
    getSearches() {
      this.$store.dispatch('getSearches')
    },
    goHome() {
      this.$router.go()
    },
    toggleMenu() {
      this.menuOpen = !this.menuOpen
    },
    logOut() {
      this.$store.dispatch('logoutUser')
      this.$router.push({ name: 'Login' })
    },
    toggleMenu() {
      this.$emit('toggle-menu')
    },
    clearText() {
      this.searchText = ''
    },
    goToIntegrations() {
      this.$router.push({ name: 'PRIntegrations' })
      this.$emit('close-menu')
    },
    goToSettings() {
      this.$router.push({ name: 'PRSettings' })
      this.$emit('close-menu')
    },
  },
  computed: {
    unfilteredSearches() {
      return this.$store.state.allSearches
    },
    searches() {
      if (this.unfilteredSearches.length) {
        return this.unfilteredSearches.filter((search) =>
          search.name.toLowerCase().includes(this.searchText.toLowerCase()),
        )
      } else return []
    },
    userName() {
      return this.$store.state.user.firstName
    },
    fullName() {
      return this.$store.state.user.fullName
    },
    isPR() {
      return this.$store.state.user.role === 'PR'
    },
    userIsLoggedIn() {
      return this.$store.getters.userIsLoggedIn
    },
    userCRM() {
      return this.$store.state.user.crm
    },
    routeName() {
      return this.$route.name
    },
    isAdmin() {
      return this.userIsLoggedIn && this.$store.state.user.isAdmin
    },
    isTeamLead() {
      return this.userIsLoggedIn && this.$store.state.user.isTeamLead
    },
    hasZoomIntegration() {
      return !!this.$store.state.user.hasZoomIntegration
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/modals';
@import '@/styles/buttons';

@media only screen and (max-width: 600px) {
}
/* Small devices (portrait tablets and large phones, 600px and up) */
@media only screen and (min-width: 600px) {
}
/* Medium devices (landscape tablets, 768px and up) */
@media only screen and (min-width: 768px) {
}
/* Large devices (laptops/desktops, 992px and up) */
@media only screen and (min-width: 992px) {
}
/* Extra large devices (large laptops and desktops, 1200px and up) */
@media only screen and (min-width: 1200px) {
}

@keyframes tooltips-horz {
  to {
    opacity: 0.9;
    transform: translate(10%, 0%);
  }
}

.rotate-img {
  transform: rotate(180deg);
}

.delete-modal {
  margin-top: 120px;
  width: 100%;
  height: 100%;
}

.delete-container {
  width: 500px;
  height: 220px;
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 14px;
  line-height: 24px;
  font-weight: 400;

  header {
    display: flex;
    flex-direction: row;
    justify-content: flex-end;

    p {
      cursor: pointer;
      margin-top: -4px;
    }
  }

  main {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    // h2 {
    //   margin-bottom: 0px;
    // }
  }
}

.v-margin {
  margin: 8px 0 !important;
}
.row {
  display: flex;
  align-items: center;
  flex-direction: row;
}

.search-icon {
  margin-left: 1rem;
  filter: invert(50%);
  cursor: pointer;
}

.beta-tag {
  letter-spacing: 1px;
  margin-left: 8px;

  p {
    background-color: $dark-black-blue;
    color: white;
    border-radius: 8px;
    padding: 2px 8px;
    font-size: 12px;
    cursor: text;

    &:hover {
      color: white;
    }
  }
}

.relative {
  position: relative;
}

.right-mar {
  margin-right: 1.25rem;
}

::placeholder {
  color: rgba(0, 0, 0, 0.4);
}

.input {
  position: sticky;
  z-index: 2005;
  top: 1.5rem;
  width: 224px;
  margin: 1.5rem 0 0.5rem 1rem;
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-family: $base-font-family;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 8px 20px 8px 10px;
}

.search-input {
  border: none;
  outline: none;
  margin-left: 0.5rem;
  width: 100%;
}

.avatar-container {
  position: relative;
}

.avatar-dropdown {
  width: 180px;
  position: absolute;
  top: 40px;
  right: -8px;
  font-size: 12px;
  font-weight: 400;
  background: white;
  padding: 1rem 0 0 0;
  border-radius: 5px;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
  z-index: 2000;
  border: 1px solid rgba(0, 0, 0, 0.1);

  p {
    margin-top: 8px;
    padding: 0;
  }
}

.searches-container::-webkit-scrollbar:hover {
}

.searches-container::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}

.searches-container::-webkit-scrollbar-thumb {
  background-color: transparent;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.searches-container:hover::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.searches-container {
  max-height: 250px;
  overflow-y: scroll;
  scroll-behavior: smooth;
  margin-bottom: 1rem;
  padding: 0.5rem 0;
}

.relative {
  position: relative;
}

.relative:hover {
  img:last-of-type {
    opacity: 1;
  }
}

.absolute-icon {
  position: absolute;
  padding-left: 4px;
  background: transparent;
  opacity: 0;
  right: 8px;
  cursor: pointer;
  &:hover {
    filter: invert(66%) sepia(47%) saturate(6468%) hue-rotate(322deg) brightness(85%) contrast(96%);
  }
}

.search-dropdown {
  width: 260px;
  position: absolute;
  top: 40px;
  right: -8px;
  font-size: 12px;
  font-weight: 400;
  background: white;
  padding: 0;
  border-radius: 5px;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
  z-index: 2001;
  border: 1px solid rgba(0, 0, 0, 0.1);

  p {
    padding: 8px 16px;
    font-size: 14px;
    color: #7c7b7b;
    cursor: pointer;
    width: 245px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    margin: 0;
  }

  p:hover {
    color: $dark-black-blue;
  }
}

.dropdown-item {
  display: flex;
  align-items: center;
  flex-direction: row;
  font-size: 14px;
  color: $dark-black-blue;
  padding: 2px 0 !important;
  padding-left: 1rem;
  cursor: pointer;
  position: relative;
  width: 100%;
  img {
    margin: 0 1.5rem 0 1.5rem;
    filter: invert(40%);
  }

  p {
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
    width: 100%;
    margin: 0;
  }

  &:hover {
    opacity: 0.65;
  }

  &__bottom {
    font-size: 14px;
    padding-top: 8px !important;
    display: flex;
    align-items: center;
    justify-content: center;
    color: $dark-black-blue;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    cursor: pointer;

    &:hover {
      opacity: 0.65;
    }
  }
}

.dropdown-border {
  padding-top: 8px !important;

  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.mar-right {
  margin-right: 23px !important;
}

.pointer {
  cursor: pointer;
}

.avatar {
  background-color: $soft-gray;
  color: $base-gray;
  font-size: 12px;
  width: 32px;
  height: 32px;
  margin-right: 4px;
  border-radius: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.left-mar {
  margin-left: 0.5rem;
  color: $dark-black-blue;
}
.nav-img {
  height: 16px;
}
div > span {
  font-size: 11px;
  color: $dark-green;
  background-color: #f3f0f0;
  margin-left: 0.25rem;
  padding: 0.2rem;
  border-radius: 0.2rem;
}
nav {
  width: 100vw;
  display: flex;
  flex-direction: row;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 2000;
  height: 58px;
  background-color: white;
  padding: 0px 4px;
  border-bottom: 1px solid $soft-gray;
}
.logo {
  cursor: pointer;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  img {
    filter: brightness(0) invert(48%) sepia(33%) saturate(348%) hue-rotate(161deg) brightness(91%)
      contrast(90%);
  }
  margin-right: 0.5rem;
}

.pointer {
  cursor: pointer;
}

.auto-left {
  margin-left: auto;
  display: flex;
  align-items: center;
  flex-direction: row;
  gap: 36px;
  font-weight: 300 !important;
  font-family: $base-font-family;
  font-size: 14px;
}

.off-gray {
  color: #6b6b6b;
}

.nav-text {
  font-weight: 400;
  font-family: $base-font-family;
  color: #6b6b6b;
  font-size: 13px;
  padding: 6px 0;
  img {
    margin-left: 8px;
  }
}

a {
  text-decoration: none;
  font-weight: 400;
  font-family: $base-font-family;
  // color: #6b6b6b;
  color: $light-gray-blue;
  font-size: 14px;
  padding: 6px 0;
  margin: 0 16px;
  img {
    transition: all 0.2s;
  }
}
a:hover {
  color: rgba(0, 0, 0, 0.5);
}
.active {
  color: #6b6b6b;
  position: relative;
  border-bottom: 1px solid $mid-gray;
}

.primary-button {
  @include dark-blue-button();
  padding: 6px 10px;
  border: none;
  img {
    filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}

.tertiary-button {
  @include dark-blue-button();
  padding: 6px 10px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  color: $dark-black-blue;
  background-color: white;
  margin-right: -2px;
  display: flex;
  flex-direction: row;
  align-items: center;
}

.red-button {
  @include dark-blue-button();
  padding: 6px 10px;
  border: 1px solid $coral;
  color: white;
  background-color: $coral;
  margin-left: 16px;
}

.templates {
  display: block;
  width: fit-content;
  height: 40px;
  position: absolute;
  top: 16px;
  left: 45%;
  font-size: 12px;
  background: $dark-green;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  pointer-events: none;
  line-height: 1.5;
  z-index: 2010;

  p {
    margin-top: 8px;
    padding: 0;
  }
}

.templates::before {
  position: absolute;
  content: '';
  height: 8px;
  width: 8px;
  background: $dark-green;
  bottom: -3px;
  left: 45%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
.wrapper {
  display: flex;
  align-items: center;
  // background-color: ;
  font-family: $thin-font-family;
  font-size: 14px;
  position: relative;
  text-align: center;
  -webkit-transform: translateZ(0); /* webkit flicker fix */
  -webkit-font-smoothing: antialiased; /* webkit text rendering fix */
}

.wrapper .tooltip {
  background: $dark-black-blue;
  border-radius: 4px;
  // bottom: 100%;
  bottom: -100%;
  color: #fff;
  display: block;
  left: -10px;
  margin-bottom: 15px;
  opacity: 0;
  padding: 8px;
  pointer-events: none;
  position: absolute;
  width: 120px;
  -webkit-transform: translateY(10px);
  -moz-transform: translateY(10px);
  -ms-transform: translateY(10px);
  -o-transform: translateY(10px);
  transform: translateY(10px);
  -webkit-transition: all 0.25s ease-out;
  -moz-transition: all 0.25s ease-out;
  -ms-transition: all 0.25s ease-out;
  -o-transition: all 0.25s ease-out;
  transition: all 0.25s ease-out;
  -webkit-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -moz-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -ms-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -o-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
}

/* This bridges the gap so you can mouse into the tooltip without it disappearing */
.wrapper .tooltip:before {
  bottom: -20px;
  content: ' ';
  display: block;
  height: 20px;
  left: 0;
  position: absolute;
  width: 100%;
}

.wrapper .tooltip:after {
  border-left: solid transparent 10px;
  border-right: solid transparent 10px;
  border-bottom: solid $dark-black-blue 10px;
  bottom: 32px;
  content: ' ';
  height: 0;
  left: 50%;
  margin-left: -13px;
  position: absolute;
  width: 0;
}

.wrapper:hover .tooltip {
  opacity: 1;
  pointer-events: auto;
  -webkit-transform: translateY(0px);
  -moz-transform: translateY(0px);
  -ms-transform: translateY(0px);
  -o-transform: translateY(0px);
  transform: translateY(0px);
}

.lte8 .wrapper .tooltip {
  display: none;
}

.lte8 .wrapper:hover .tooltip {
  display: block;
}
</style>
