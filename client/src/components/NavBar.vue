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
    <Modal v-if="plansModal" class="pricing-modal">
      <div class="pricing-container">
        <header @click="closePlansModal">
          <p>X</p>
        </header>
        <main>
          <h2 class="pricing-header">Upgrade to PRO</h2>
          <p>This plan includes unlimited usage, email alerts, and premium support</p>
          <div class="pricing-box">
            <!-- <h2 class="pricing-box__header">PRO</h2> -->
            <!-- <p>Self-serve plan with unlimited usage, automated email summaries, and the ability to learn your writing style.</p> -->
            <!-- <p>Upgrade to unlimited usage and additional AI automations</p> -->
            <h1 class="pricing-price">$80 <span class="pricing-smaller-text">per user / month</span></h1>
            <div>
              <div class="pricing-list-container">
                <h3 class="pricing-list-header">Everything in free, plus:</h3>
                <ul class="pricing-list">
                  <li>Unlimited usage</li>
                  <li>Daily email alerts</li>
                  <li>Personalized writing style</li>
                  <li>Shareable digest</li>
                  <!-- <li>AI call summaries</li> -->
                  <li>Onboarding & Training</li>
                  <li>Dedicated Customer Success Manager</li>
                  <li>User data does not train comercial AI models</li>
                </ul>
              </div>
              <div class="display-flex display-center pricing-width pricing-users relative">
                <p class="users-position">Select number of users: </p>
                <Multiselect
                  style="width: 100%; height: 0.5rem; margin-left: 0.0rem;"
                  :options="amountList"
                  :show-labels="false"
                  v-model="numberOfUsers"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results.</p>
                  </template>
                </Multiselect>
              </div>
              <button @click="purchasePro" class="primary-button pricing-button">Upgrade to PRO <img src="@/assets/images/arrow-small-right.svg" class="pricing-arrow-right" /></button>
              <!-- <p class="gray-text">This is a one-time fee. Training and premium support included.</p> -->
            </div>
          </div>
          <p class="gray-text">Questions about PRO plan or billing? <a href="mailto:customers@managr.ai" style="font-size: 11px; margin: 0;">Contact us.</a></p>

          <!-- <div class="display-flex display-center pricing-width pricing-users">
            <p>Number of Users: </p>
            <Multiselect
              style="margin-left: 1rem; width: 80px; height: 0.5rem;"
              :options="amountList"
              :show-labels="false"
              v-model="numberOfUsers"
            >
              <template slot="noResult">
                <p class="multi-slot">No results.</p>
              </template>
            </Multiselect>
          </div> -->

          <!-- <div class="pricing-width">
            <p>Amount: ${{ 80 * 12 * numberOfUsers }}</p>
          </div> -->

          <!-- <div class="pricing-width">
            <p class="gray-text">Questions about plan or billing? <a href="customers@managr.ai">Contact us.</a></p>
          </div> -->

          <!-- <div style="margin-top: 20px" class="row">
            <button @click="closePlansModal" class="tertiary-button">Cancel</button>
            <button @click="purchasePro" class="primary-button">Upgrade</button>
          </div> -->
        </main>
      </div>
    </Modal>
    <Modal v-if="deletePitchModelOpen" class="delete-modal">
      <div class="delete-container">
        <header @click="togglePitchDeleteModal">
          <p>X</p>
        </header>
        <main>
          <h2>Delete Pitch</h2>
          <p>Are you sure you want to delete this pitch ?</p>

          <div style="margin-top: 20px" class="row">
            <button @click="togglePitchDeleteModal" class="tertiary-button">Cancel</button>
            <button @click="deletePitch" class="red-button">Delete</button>
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
      <nav id="nav" v-if="this.$store.state.user.role === 'PR' && !isMobile">
        <router-link :to="{ name: 'PRSummaries' }">
          <div class="logo">
            <img @click="goHome" style="height: 28px" src="@/assets/images/logo.png" />
            <div class="beta-tag">
              <p id="pro-free-version" :class="!isPaid ? 'pointer' : ''" @click="openPlansModal">{{ isPaid ? 'PRO' : 'Upgrade Plan' }}</p>
            </div>
          </div>
        </router-link>

        <router-link active-class="active" :to="{ name: 'PRSummaries' }" id="router-summarize">
          <p>Search</p>
        </router-link>

        <router-link active-class="active" :to="{ name: 'Pitches' }" id="router-pitch">
          <p>Pitch</p>
        </router-link>

        <!-- <router-link
          v-if="!hasZoomIntegration"
          :to="{ name: 'PRIntegrations' }"
          id="router-transcribe1"
        >
          <div class="wrapper">
            <p>Transcribe</p>
            <div style="margin-left: -20px" class="tooltip">Connect Zoom</div>
          </div>
        </router-link>

        <router-link
          v-else
          active-class="active"
          :to="{ name: 'PRTranscripts' }"
          id="router-transcribe2"
        >
          <p>Transcribe</p>
        </router-link> -->

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

          <div
            v-if="($route.name === 'PRSummaries' || $route.name === 'Pitches') && !isPaid"
            class="row wrapper-count"
          >
            <p class="searches-used-text">{{ searchesUsed }} / 10</p>
            <div style="margin-left: -40px" class="tooltip-count">Remaining monthly credits</div>
          </div>
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

            <div
              v-else-if="$route.name === 'Pitches'"
              @click="toggleShowPitches"
              class="row pointer nav-text"
            >
              Saved Pitches
              <img
                v-if="!showSavedPitches"
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
                    @click="selectSearch(search)"
                  />
                  <img
                    class="search-icon"
                    v-else-if="search.type === 'SOCIAL_MEDIA'"
                    src="@/assets/images/comment.svg"
                    height="12px"
                    alt=""
                    @click="selectSearch(search)"
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
            <div v-if="showSavedPitches" class="search-dropdown">
              <div class="input">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                  <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M4.1 11.06a6.95 6.95 0 1 1 13.9 0 6.95 6.95 0 0 1-13.9 0zm6.94-8.05a8.05 8.05 0 1 0 5.13 14.26l3.75 3.75a.56.56 0 1 0 .8-.79l-3.74-3.73A8.05 8.05 0 0 0 11.04 3v.01z"
                    fill="currentColor"
                  ></path>
                </svg>
                <input class="search-input" v-model="pitchText" :placeholder="`Search...`" />
                <img
                  v-show="pitchText"
                  @click="clearText"
                  src="@/assets/images/close.svg"
                  class="invert pointer"
                  height="12px"
                  alt=""
                />
              </div>
              <p class="v-margin" v-if="!pitches.length">Nothing here...</p>

              <div class="searches-container">
                <div
                  @mouseenter="setIndex(i)"
                  @mouseLeave="removeIndex"
                  class="row relative"
                  v-for="(pitch, i) in pitches"
                  :key="pitch.id"
                >
                  <img
                    class="search-icon invert"
                    v-if="pitch.type === 'NEWS'"
                    src="@/assets/images/memo.svg"
                    height="12px"
                    alt=""
                    @click="selectPitch(pitch)"
                  />
                  <img
                    class="search-icon"
                    v-else-if="pitch.type === 'SOCIAL_MEDIA'"
                    src="@/assets/images/comment.svg"
                    height="12px"
                    alt=""
                    @click="selectPitch(pitch)"
                  />
                  <p @click="selectPitch(pitch)">
                    {{ pitch.name }}
                  </p>

                  <img
                    @click="togglePitchDeleteModal(pitch)"
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
                <img class="mar-right" src="@/assets/images/profile.svg" height="13px" alt="" />
                Users
              </p>
              <p class="dropdown-item" @click="goToIntegrations">
                <img class="mar-right" src="@/assets/images/apps.svg" height="13px" alt="" />
                Integrations
              </p>
              <p class="dropdown-item" @click="goToReports">
                <img class="mar-right" src="@/assets/images/report.svg" height="13px" alt="" />
                Digest
              </p>
              <p @click="logOut" class="dropdown-item dropdown-border">
                <img class="mar-right" src="@/assets/images/logout.svg" height="13px" alt="" /> Sign
                out
              </p>
            </div>
          </div>
        </div>
      </nav>
      <div v-else-if="this.$store.state.user.role === 'PR' && isMobile" class="hamburger-container">
        <img src="@/assets/images/menu-burger.svg" class="hamburger" @click="showMobileMenu" />
      </div>
      <nav v-if="mobileMenuOpen" class="mobile-nav-container" v-clickOutsideMobileNav>
        <div @click="goHome" class="mobile-nav-top mar-left extra-padding-vert">
          <p class="small-margin">Home</p>
        </div>

        <router-link active-class="active" :to="{ name: 'PRSummaries' }">
          <p class="small-margin">Search</p>
        </router-link>

        <router-link active-class="active" :to="{ name: 'Pitches' }">
          <p class="small-margin">Pitch</p>
        </router-link>

        <!-- <div v-if="!hasZoomIntegration" :to="{ name: 'PRIntegrations' }">
          <div class="wrapper-mobile">
            <p class="small-margin light-gray-blue">Transcribe</p>
            <div style="margin-left: -20px" class="tooltip-mobile">Connect Zoom</div>
          </div>
        </div>

        <router-link v-else active-class="active" :to="{ name: 'PRTranscripts' }">
          <p class="small-margin">Transcribe</p>
        </router-link> -->

        <div class="relative mar-left">
          <div
            v-if="$route.name === 'PRSummaries'"
            @click="toggleShowSearches"
            class="row pointer nav-text saved-searches-mobile"
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
          <div
            v-else-if="$route.name === 'Pitches'"
            @click="toggleShowPitches"
            class="row pointer nav-text saved-searches-mobile"
          >
            Saved Pitches
            <img
              v-if="!showSavedPitches"
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

          <!-- search-dropdown -->
          <div v-if="showSavedSearches" class="">
            <!-- <div class="input">
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
            <p class="v-margin" v-if="!searches.length">Nothing here...</p> -->

            <div class="searches-container">
              <div
                @mouseenter="setIndex(i)"
                @mouseLeave="removeIndex"
                class="row relative"
                v-for="(search, i) in searches"
                :key="search.id"
              >
                <img
                  class="search-icon mobile-search-icon invert"
                  v-if="search.type === 'NEWS'"
                  src="@/assets/images/memo.svg"
                  height="12px"
                  alt=""
                />
                <img
                  class="search-icon mobile-search-icon"
                  v-else-if="search.type === 'SOCIAL_MEDIA'"
                  src="@/assets/images/comment.svg"
                  height="12px"
                  alt=""
                />
                <p @click="selectSearch(search)" class="light-gray-blue">
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
          <div v-else-if="showSavedPitches">
            <div class="searches-container">
              <div
                @mouseenter="setIndex(i)"
                @mouseLeave="removeIndex"
                class="row relative"
                v-for="(pitch, i) in pitches"
                :key="pitch.id"
              >
                <img
                  class="search-icon mobile-search-icon invert"
                  v-if="pitch.type === 'NEWS'"
                  src="@/assets/images/memo.svg"
                  height="12px"
                  alt=""
                  @click="selectPitch(pitch)"
                />
                <img
                  class="search-icon mobile-search-icon"
                  v-else-if="pitch.type === 'SOCIAL_MEDIA'"
                  src="@/assets/images/comment.svg"
                  height="12px"
                  alt=""
                  @click="selectPitch(pitch)"
                />
                <p @click="selectPitch(pitch)" class="light-gray-blue">
                  {{ pitch.name }}
                </p>

                <img
                  @click="togglePitchDeleteModal(pitch)"
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

        <router-link active-class="active" :to="{ name: 'PRSettings' }">
          <!-- <img class="mar-right" src="@/assets/images/settings.svg" height="14px" alt="" /> -->
          <!-- <img class="mar-right" src="@/assets/images/profile.svg" height="14px" alt="" /> -->
          Users
        </router-link>
        <router-link active-class="active" :to="{ name: 'PRIntegrations' }">
          <!-- <img class="mar-right" src="@/assets/images/apps.svg" height="14px" alt="" /> -->
          Integrations
        </router-link>
        <router-link active-class="active" :to="{ name: 'PRReports' }">
          <!-- <img class="mar-right" src="@/assets/images/report.svg" height="14px" alt="" /> -->
          Reports
        </router-link>
        <div active-class="active" @click="logOut" class="bottom">
          <img class="minor-mar-right" src="@/assets/images/logout.svg" height="12px" alt="" /> Sign
          out
        </div>
      </nav>
    </div>
  </div>
</template>

<script>
import { CollectionManager } from '@thinknimble/tn-models'
import { Comms } from '@/services/comms'
import { Store } from 'vuex'
import User from '@/services/users'

export default {
  name: 'NavBar',
  components: {
    CollectionManager,
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  props: {
    menuOpen: { type: Boolean },
  },
  data() {
    return {
      items: [],
      searchText: '',
      pitchText: '',
      showSavedSearches: false,
      showSavedPitches: false,
      deleteModelOpen: false,
      deletePitchModelOpen: false,
      selectedSearch: null,
      selectedPich: null,
      soonText: 'Transcribe',
      hoverIndex: null,
      showUpdateBanner: false,
      mobileMenuOpen: false,
      hamburgerClicked: false,
      plansModal: false,
      team: CollectionManager.create({ ModelClass: User }),
      numberOfUsers: 5,
      amountList: [
          1,
          2,
          3,
          4,
          5,
          6,
          7,
          8,
          9,
          10,
          11,
          12,
          13,
          14,
          15,
          16,
          17,
          18,
          19,
          20,
          21,
          22,
          23,
          24,
          25,
          26,
          27,
          28,
          29,
          30,
          31,
          32,
          33,
          34,
          35,
          36,
          37,
          38,
          39,
          40,
          41,
          42,
          43,
          44,
          45,
          46,
          47,
          48,
          49,
          50,
          51,
          52,
          53,
          54,
          55,
          56,
          57,
          58,
          59,
          60,
          61,
          62,
          63,
          64,
          65,
          66,
          67,
          68,
          69,
          70,
          71,
          72,
          73,
          74,
          75,
          76,
          77,
          78,
          79,
          80,
          81,
          82,
          83,
          84,
          85,
          86,
          87,
          88,
          89,
          90,
          91,
          92,
          93,
          94,
          95,
          96,
          97,
          98,
          99,
          100
      ],
    }
  },
  async created() {
    this.getSearches()
    this.getPitches()
    await this.team.refresh()
    this.amountList = this.amountList.filter(item => item >= this.activeUsers.length)
    this.numberOfUsers = this.activeUsers.length
  },
  directives: {
    clickOutsideMobileNav: {
      bind(el, binding, vnode) {
        // Define a function to handle click events
        function clickOutsideHandler(e) {
          // Check if the clicked element is outside the target element
          if (!el.contains(e.target)) {
            // Trigger the provided method from the binding value
            if (vnode.context.mobileMenuOpen && !vnode.context.hamburgerClicked) {
              vnode.context.hideMobileMenu()
            }
            vnode.context.hamburgerClicked = false
          }
        }

        // Add a click event listener to the document body
        document.body.addEventListener('click', clickOutsideHandler)

        // Store the event listener on the element for cleanup
        el._clickOutsideHandler = clickOutsideHandler
      },
      unbind(el) {
        // Remove the event listener when the directive is unbound
        document.body.removeEventListener('click', el._clickOutsideHandler)
      },
    },
  },
  watch: {
    $route(to, from) {
      this.hideMobileMenu()
      this.showSavedPitches = false
      this.showSavedSearches = false
      this.$emit('close-menu')
    },
  },
  methods: {
    setIndex(i) {
      this.hoverIndex = i
    },
    removeIndex() {
      this.hoverIndex = null
    },
    showMobileMenu() {
      this.hamburgerClicked = true
      this.mobileMenuOpen = true
    },
    hideMobileMenu() {
      this.mobileMenuOpen = false
    },
    openPlansModal() {
      if (!this.isPaid) {
        this.plansModal = true
      }
    },
    closePlansModal() {
      this.plansModal = false
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
      this.showSavedPitches = false
    },
    togglePitchDeleteModal(pitch = null) {
      if (pitch) {
        this.selectedPitch = pitch
      }
      this.deletePitchModelOpen = !this.deletePitchModelOpen
      this.showSavedSearches = false
      this.showSavedPitches = false
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
    async deletePitch() {
      try {
        await Comms.api
          .deletePitch({
            id: this.selectedPitch.id,
          })
          .then(() => {
            this.$store.dispatch('getPitches')
            this.deletePitchModelOpen = false
            this.showUpdateBanner = true
          })
      } catch (e) {
        console.log('ERROR DELETING PITCH', e)
      } finally {
        setTimeout(() => {
          this.showUpdateBanner = false
        }, 2000)
      }
    },
    getInitials() {
      const fullSplit = this.fullName.split(' ')
      let initials = ''
      fullSplit.forEach((word) => {
        if (word[0]) {
          return (initials += word[0])
        }
      })
      return initials
    },
    async purchasePro() {
      try {
        const response = await User.api.upgrade({ quantity: this.numberOfUsers })
        const sessionId = response.session_id;

        const stripe = await this.$stripe();

        const result = await stripe.redirectToCheckout({
          sessionId: sessionId,
        });

        if (result.error) {
          console.log('error', result.error)
        }
        this.numberOfUsers = 5
      } catch(e) {
        console.log('Error in purchasePro: ', e)
      }
    },
    selectSearch(search) {
      this.toggleShowSearches()
      this.$store.dispatch('setSearch', search)
    },
    selectPitch(pitch) {
      this.toggleShowPitches()
      this.$store.dispatch('setPitch', pitch)
    },
    toggleShowSearches() {
      this.$emit('close-menu')
      this.showSavedSearches = !this.showSavedSearches
    },
    toggleShowPitches() {
      this.$emit('close-menu')
      this.showSavedPitches = !this.showSavedPitches
    },
    getSearches() {
      this.$store.dispatch('getSearches')
    },
    getPitches() {
      this.$store.dispatch('getPitches')
    },
    goHome() {
      this.$router.go()
    },
    logOut() {
      this.$store.dispatch('logoutUser')
      localStorage.removeItem('token')
      localStorage.removeItem('tokenReceivedAt')
      this.$router.push({ name: 'Login' })
      this.hideMobileMenu()
    },
    toggleMenu() {
      this.showSavedPitches = false
      this.showSavedSearches = false
      this.$emit('toggle-menu')
    },
    clearText() {
      this.searchText = ''
      this.pitchText = ''
    },
    goToIntegrations() {
      this.$router.push({ name: 'PRIntegrations' })
      this.$emit('close-menu')
    },
    goToReports() {
      this.$router.push({ name: 'PRReports' })
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
    activeUsers() {
      return this.team.list.filter(user => user.isActive)
    },
    unfilteredPitches() {
      return this.$store.state.allPitches
    },
    searches() {
      if (this.unfilteredSearches.length) {
        return this.unfilteredSearches.filter((search) =>
          search.name.toLowerCase().includes(this.searchText.toLowerCase()),
        )
      } else return []
    },
    pitches() {
      if (this.unfilteredPitches.length) {
        return this.unfilteredPitches.filter((pitch) =>
          pitch.name.toLowerCase().includes(this.pitchText.toLowerCase()),
        )
      } else return []
    },
    isMobile() {
      return window.innerWidth <= 600
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
    isPaid() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return !!this.$store.state.user.organizationRef.isPaid
    },
    searchesUsed() {
      let arr = []
      let currentMonth = new Date(Date.now()).getMonth() + 1
      if (currentMonth < 10) {
        currentMonth = `0${currentMonth}`
      } else {
        currentMonth = `${currentMonth}`
      }
      let currentYear = new Date(Date.now()).getFullYear()
      for (let key in this.$store.state.user.metaData) {
        const item = this.$store.state.user.metaData[key]
        const filteredByMonth = item.timestamps.filter((date) => {
          const split = date.split('-')
          return split[1] == currentMonth && split[0] == currentYear
        })
        arr = [...arr, ...filteredByMonth]
      }
      return arr.length
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

.pricing-modal {
  margin-top: 70px;
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

.pricing-container {
  width: 45vw;
  height: 80vh;
  // color: $base-gray;
  color: $dark-black-blue;
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

.mobile-search-icon {
  filter: invert(65%) sepia(13%) saturate(505%) hue-rotate(200deg) brightness(90%) contrast(88%);
}

.beta-tag {
  letter-spacing: 1px;
  margin-left: 32px;

  p {
    background-color: $dark-black-blue;
    color: white;
    border-radius: 8px;
    padding: 2px 8px 4px 8px;
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
  font-family: $thin-font-family;
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
  @media only screen and (max-width: 600px) {
    font-size: 13px;
    p {
      margin-left: 0.5rem;
    }
  }
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
    margin: 0 0.5rem 0 1.5rem;
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

.minor-mar-right {
  margin-right: 6px !important;
  margin-left: 6px;
}

.pointer {
  cursor: pointer !important;
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
  @media only screen and (max-width: 600px) {
    align-items: flex-start;
  }
}
.hamburger-container {
  z-index: 2000;
  height: 58px;
  width: 100vw;
  background-color: white;
}
.hamburger {
  height: 20px;
  margin: 1.5rem 2rem;
}
.mobile-nav-container {
  z-index: 2000;
  height: 100vh;
  width: 80vw;
  border-right: 1px solid $soft-gray;
  background-color: white;
  display: flex;
  flex-direction: column;
}
.logo {
  cursor: pointer;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  img {
    // filter: brightness(0) invert(48%) sepia(33%) saturate(348%) hue-rotate(161deg) brightness(91%)
    //   contrast(90%);
    filter: brightness(0) invert(23%) sepia(19%) saturate(984%) hue-rotate(162deg) brightness(92%)
      contrast(87%);
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
  font-family: $thin-font-family;
  font-size: 14px;
  @media only screen and (max-width: 600px) {
    gap: 4px;
  }
}

.off-gray {
  color: #6b6b6b;
}

.nav-text {
  font-weight: 400;
  font-family: $thin-font-family;
  color: #6b6b6b;
  font-size: 13px;
  padding: 6px 0;
  @media only screen and (max-width: 600px) {
    padding: 14px 0;
    color: $dark-black-blue;
    // font-size: 18px;
  }
  img {
    margin-left: 8px;
  }
}
.light-gray-blue {
  color: $light-gray-blue;
}
.saved-searches-mobile {
  @media only screen and (max-width: 600px) {
    font-size: 14px;
    color: $dark-black-blue;
  }
}
a {
  text-decoration: none;
  font-weight: 400;
  font-family: $thin-font-family;
  // color: #6b6b6b;
  color: $light-gray-blue;
  font-size: 14px;
  padding: 6px 4px;
  margin: 0 12px;
  @media only screen and (max-width: 600px) {
    margin: 0px 16px;
    padding: 14px 0;
    color: $dark-black-blue;
    // font-size: 18px;
  }
  img {
    transition: all 0.2s;
  }
}
a:hover {
  color: rgba(0, 0, 0, 0.5);
}
.active {
  color: $dark-black-blue;
  position: relative;
  border-bottom: 2px solid $dark-black-blue;
  // background-color: $white-blue;
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

.wrapper-count {
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

.wrapper-count .tooltip-count {
  background: $dark-black-blue;
  border-radius: 4px;
  // bottom: 100%;
  bottom: -100%;
  color: #fff;
  display: block;
  left: -20px;
  margin-bottom: 15px;
  opacity: 0;
  padding: 8px;
  pointer-events: none;
  position: absolute;
  width: 175px;
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

/* This bridges the gap so you can mouse into the tooltip-count without it disappearing */
.wrapper-count .tooltip-count:before {
  bottom: -20px;
  content: ' ';
  display: block;
  height: 20px;
  left: 0;
  position: absolute;
  width: 100%;
}

.wrapper-count .tooltip-count:after {
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

.wrapper-count:hover .tooltip-count {
  opacity: 1;
  pointer-events: auto;
  -webkit-transform: translateY(0px);
  -moz-transform: translateY(0px);
  -ms-transform: translateY(0px);
  -o-transform: translateY(0px);
  transform: translateY(0px);
}

.lte8 .wrapper-count .tooltip-count {
  display: none;
}

.lte8 .wrapper-count:hover .tooltip-count {
  display: block;
}
.wrapper-mobile {
  display: flex;
  align-items: center;
  // background-color: ;
  font-family: $thin-font-family;
  font-size: 14px;
  position: relative;
  text-align: center;
  -webkit-transform: translateZ(0); /* webkit flicker fix */
  -webkit-font-smoothing: antialiased; /* webkit text rendering fix */
  margin-left: 1rem;
  padding: 10px 0;
}

.wrapper-mobile .tooltip-mobile {
  background: $dark-black-blue;
  border-radius: 4px;
  // bottom: 100%;
  bottom: -40%;
  color: #fff;
  display: block;
  left: 90px;
  margin-bottom: 15px;
  opacity: 0;
  padding: 8px;
  pointer-events: none;
  position: absolute;
  width: 125px;
  -webkit-transform: translateX(0px);
  -moz-transform: translateX(0px);
  -ms-transform: translateX(0px);
  -o-transform: translateX(0px);
  transform: translateX(0px);
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

/* This bridges the gap so you can mouse into the tooltip-mobile without it disappearing */
.wrapper-mobile .tooltip-mobile:before {
  bottom: -20px;
  content: ' ';
  display: block;
  height: 20px;
  left: 0;
  position: absolute;
  width: 100%;
}

.wrapper-mobile .tooltip-mobile:after {
  border-right: solid $dark-black-blue 10px;
  border-left: solid transparent 10px;
  border-bottom: solid transparent 10px;
  border-top: solid transparent 10px;
  bottom: 20%;
  content: ' ';
  height: 0;
  left: -5%;
  margin-left: -13px;
  position: absolute;
  width: 0;
}

.wrapper-mobile:hover .tooltip-mobile {
  opacity: 1;
  pointer-events: auto;
  -webkit-transform: translateX(10px);
  -moz-transform: translateX(10px);
  -ms-transform: translateX(10px);
  -o-transform: translateX(10px);
  transform: translateX(10px);
}

.lte8 .wrapper-mobile .tooltip-mobile {
  display: none;
}

.lte8 .wrapper-mobile:hover .tooltip-mobile {
  display: block;
}
.searches-used-text {
  background-color: #e8f2fa;
  padding: 0.35rem;
  border-radius: 0.25rem;
  color: $dark-black-blue;
  font-size: 12px;
}

.small-margin {
  margin: 0rem 0;
}
.extra-padding-vert {
  padding: 14px 0;
  font-size: 14px;
}
.mobile-nav-top {
  margin-top: 2rem;
}
.mar-left {
  margin-left: 1rem;
}
.bottom {
  position: absolute;
  bottom: 30px;
  font-size: 14px;
  color: $dark-black-blue;
}
.display-flex {
  display: flex;
}
.display-center {
  align-items: center;
}
.gray-text {
  color: $mid-gray;
  font-size: 11px;
}
.pricing-width {
  width: 100%;
}
.pricing-box {
  border: 1px solid $soft-gray;
  border-radius: 0.5rem;
  width: 65%;
  // padding: 0.5rem 0.75rem;
  padding: 1rem 1.5rem;
  margin: 1rem 0;
  &__header {
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
    font-size: 24px;
  }
}
.pricing-price {
  // margin-top: 0.5rem;
  // margin-bottom: 0.5rem;
}
.pricing-smaller-text {
  font-size: 13px;
}
.pricing-header {
  margin-top: 0;
}
.pricing-list-header {
  margin-top: 0.25rem;
  margin-bottom: 0.25rem;
}
.pricing-list {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  padding-left: 1rem;
  // padding-bottom: 1rem;
  // border-bottom: 1px solid $soft-gray;
}
.pricing-users {
  border-top: 1px solid $soft-gray;
  margin-top: 0rem;
  // padding-top: 1rem;
  padding: 0.85rem 0 0.5rem 0;
}
.pricing-button {
  width: 100%;
  padding: 0.75rem;
  margin: 0.5rem 0 !important;
}
.pricing-list-container {
  height: 26vh;
  overflow: auto;
}
.pricing-arrow-right {
  height: 14px;
  margin-left: 0.25rem;
  filter: invert(99%) !important;
}
.relative {
  position: relative;
}
.users-position {
  position: absolute;
  z-index: 9999;
  // margin-bottom: 0;
}
// ::v-deep .multiselect {
//   min-height: 30px;
// }
::v-deep .multiselect * {
  font-size: 14px;
  font-family: $thin-font-family;
  // border-radius: 5px !important;
}
::v-deep .multiselect__option--highlight {
  background-color: $off-white;
  color: $base-gray;
}
::v-deep .multiselect__option--selected {
  background-color: $soft-gray;
}

::v-deep .multiselect__content-wrapper {
  // border-radius: 5px;
  margin: 0.5rem 0rem;
  border-top: 1px solid $soft-gray;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  position: absolute !important;
}

::v-deep .multiselect__tags {
  border: none;
  border-bottom: 1px solid rgba(0, 0, 0, 0.15) !important;
  border-radius: 0;
  padding-left: 8.8rem;
  padding-top: 0.65rem;
  padding-bottom: 0.0rem;
  min-height: 25px;
}

::v-deep .multiselect__select {
  height: 32px;
}

::v-deep .multiselect__single {
  margin-bottom: 0;
}

::v-deep .multiselect__placeholder {
  color: $base-gray;
}
</style>
