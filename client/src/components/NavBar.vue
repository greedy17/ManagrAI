<template>
  <div>
    <Modal v-if="deleteModelOpen" class="delete-modal">
      <div class="delete-container">
        <header @click="toggleDeleteModal">
          <img src="@/assets/images/close.svg" height="18px" alt="" />
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
    <Modal v-if="deleteReportModalOpen" class="delete-modal">
      <div class="delete-container">
        <header @click="toggleReportDeleteModal">
          <img src="@/assets/images/close.svg" height="18px" alt="" />
        </header>
        <main>
          <h2>Delete Report</h2>
          <p>Are you sure you want to delete this report ?</p>

          <div style="margin-top: 20px" class="row">
            <button @click="toggleReportDeleteModal" class="tertiary-button">Cancel</button>
            <button @click="deleteReport" class="red-button">Delete</button>
          </div>
        </main>
      </div>
    </Modal>
    <Modal v-if="plansModal" class="pricing-modal">
      <div class="pricing-container">
        <header @click="closePlansModal">
          <img src="@/assets/images/close.svg" height="18px" alt="" />
        </header>
        <main>
          <h2 class="pricing-header">Upgrade to PRO</h2>
          <!-- <p>This plan includes unlimited usage, email alerts, and premium support</p> -->
          <div class="pricing-box">
            <!-- <h2 class="pricing-box__header">PRO</h2> -->
            <!-- <p>Self-serve plan with unlimited usage, automated email summaries, and the ability to learn your writing style.</p> -->
            <!-- <p>Upgrade to unlimited usage and additional AI automations</p> -->
            <h1 class="pricing-price">
              $133.33 <span class="pricing-smaller-text">per user / month</span>
            </h1>
            <div>
              <div class="pricing-list-container">
                <h3 class="pricing-list-header">Everything in free, plus:</h3>
                <ul class="pricing-list">
                  <li>Unlimited usage</li>
                  <li>Unlimited saved searches</li>
                  <li>Daily email alerts</li>
                  <li>Unlimited list building</li>
                  <li>Onboarding</li>
                  <li>Premium support</li>
                  <!-- <li>Dedicated Customer Success Manager</li>
                  <li>User data does not train comercial AI models</li> -->
                </ul>
              </div>
              <div class="display-flex display-center pricing-width pricing-users relative">
                <p class="users-position">Select number of users:</p>
                <Multiselect
                  style="width: 100%; height: 0.5rem; margin-left: 0rem"
                  :options="amountList"
                  :show-labels="false"
                  v-model="numberOfUsers"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results.</p>
                  </template>
                </Multiselect>
              </div>
              <button @click="purchasePro" class="primary-button pricing-button">
                Upgrade to PRO
                <img src="@/assets/images/arrow-small-right.svg" class="pricing-arrow-right" />
              </button>
              <!-- <p class="gray-text">This is a one-time fee. Training and premium support included.</p> -->
            </div>
          </div>
          <p class="gray-text">Have questions ? Email us at mike@mymanagr.com</p>

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

    <Modal v-if="reportsModalOpen" class="paid-modal">
      <div class="regen-container">
        <div class="paid-header">
          <div>
            <h4 class="regen-header-title"></h4>
            <p class="regen-header-subtitle"></p>
          </div>
        </div>
        <div class="paid-body">
          <div>
            <div class="paid-center">
              <h3 class="paid-title">Add Coverage Reports</h3>

              <h5 class="regen-body-title">Contact us to purchase Coverage Report credits.</h5>
            </div>
          </div>
        </div>
        <div style="height: 100px" class="paid-footer">
          <div class="row">
            <div class="save-button" @click="purchaseCredits">Contact</div>
          </div>
        </div>
      </div>
    </Modal>

    <!-- <Modal v-if="reportsModalOpen" class="pricing-modal">
      <div style="height: 420px" class="pricing-container">
       
        <main style="margin-top: 12px">
          <h2 class="bold-txt large-txt">Add coverage reports</h2>
          <div class="pricing-box">
            <p class="small-bold-text">You do not have any <span>Coverage Report credits</span></p>
            <div>
              <div style="height: 100px" class="pricing-list-container bold-txt">
                <p>Purchase credits by clicking Upgrade Account.</p>
              </div>

              <button
                style="font-size: 14px"
                @click="purchaseCredits"
                class="primary-button pricing-button"
              >
                Upgrade Account
              </button>
            </div>
          </div>
          <p class="gray-text">Have questions ? Email us at mike@mymanagr.com</p>
        </main>
      </div>
    </Modal> -->

    <Modal v-if="deletePitchModelOpen" class="delete-modal">
      <div class="delete-container">
        <header @click="togglePitchDeleteModal">
          <img src="@/assets/images/close.svg" height="18px" alt="" />
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
    <Modal v-if="deleteAssistModelOpen" class="delete-modal">
      <div class="delete-container">
        <header @click="toggleAssistDeleteModal">
          <img src="@/assets/images/close.svg" height="18px" alt="" />
        </header>
        <main>
          <h2>Delete Assist</h2>
          <p>Are you sure you want to delete this Assist ?</p>

          <div style="margin-top: 20px" class="row">
            <button @click="toggleAssistDeleteModal" class="tertiary-button">Cancel</button>
            <button @click="deleteProcess" class="red-button">Delete</button>
          </div>
        </main>
      </div>
    </Modal>
    <Modal v-if="deleteDiscoveryModelOpen" class="delete-modal">
      <div class="delete-container">
        <header @click="toggleDiscoveryDeleteModal">
          <img src="@/assets/images/close.svg" height="18px" alt="" />
        </header>
        <main>
          <h2>Delete List</h2>
          <p>Are you sure you want to delete this List ?</p>

          <div style="margin-top: 20px" class="row">
            <button @click="toggleDiscoveryDeleteModal" class="tertiary-button">Cancel</button>
            <button @click="deleteDiscovery" class="red-button">Delete</button>
          </div>
        </main>
      </div>
    </Modal>
    <Transition name="slide-fade">
      <div v-if="showUpdateBanner" class="templates">
        <p>Search successfully deleted!</p>
      </div>
    </Transition>
    <div v-if="userIsLoggedIn || isViewOnly">
      <div id="hamburger">
        <img
          v-if="!mobileMenuOpen && !isViewOnly"
          src="@/assets/images/menu-burger.svg"
          height="24px"
          @click="toggleMobileMenu"
        />
        <div class="close-menu" @click="toggleMobileMenu" v-else>X</div>
      </div>

      <div class="mobile-nav" v-if="mobileMenuOpen && !isViewOnly">
        <router-link
          active-class="active-mobile"
          :to="{ name: 'PRSummaries' }"
          id="router-summarize"
        >
          <p>Threads</p>
        </router-link>
        <router-link active-class="active-mobile" :to="{ name: 'Contacts' }" id="router-pitch">
          <p>Contacts</p>
        </router-link>

        <router-link active-class="active-mobile" :to="{ name: 'EmailTracking' }" id="router-pitch">
          <p>Emails</p>
        </router-link>
        <router-link active-class="active-mobile" :to="{ name: 'PRSettings' }" id="router-pitch">
          <p>Settings</p>
        </router-link>
        <p style="text-align: center" @click="logOut">Logout</p>
      </div>

      <div v-if="$route.name === 'PRSummaries' && !isViewOnly" id="relative-mobile">
        <div>
          <div @click.stop="toggleShowSearches" class="row pointer nav-text">
            Saved Threads
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

          <div v-show="showSavedSearches" class="search-dropdown">
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
                  v-if="search.meta_data.type === 'news'"
                  src="@/assets/images/globe.svg"
                  height="12px"
                  alt=""
                  @click="selectSearch(search)"
                />
                <img
                  class="search-icon"
                  v-else-if="search.meta_data.type === 'social'"
                  src="@/assets/images/thumb.svg"
                  height="12px"
                  alt=""
                  @click="selectSearch(search)"
                />
                <img
                  class="search-icon"
                  v-else-if="search.meta_data.type === 'web'"
                  src="@/assets/images/google.svg"
                  height="12px"
                  alt=""
                  @click="selectSearch(search)"
                />
                <img
                  class="search-icon"
                  v-else-if="search.meta_data.type === 'discover'"
                  src="@/assets/images/users.svg"
                  height="12px"
                  alt=""
                  @click="selectSearch(search)"
                />
                <img
                  class="search-icon"
                  v-else-if="search.meta_data.type === 'write'"
                  src="@/assets/images/brain.svg"
                  height="12px"
                  alt=""
                  @click="selectSearch(search)"
                />
                <img
                  class="search-icon"
                  v-else-if="search.meta_data.type === 'trending'"
                  src="@/assets/images/arrow-trend-up.svg"
                  height="12px"
                  alt=""
                  @click="selectSearch(search)"
                />
                <p :title="search.title" @click="selectSearch(search)">
                  {{ search.title }}
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
      </div>

      <nav id="nav">
        <div style="margin-left: 12px" @click="goHome" class="row">
          <div class="logo">
            <img style="height: 28px" src="@/assets/images/newLogo.png" />
          </div>
        </div>

        <router-link active-class="active" :to="{ name: 'PRSummaries' }" id="router-summarize">
          <p>Threads</p>
        </router-link>

        <router-link
          v-if="!isViewOnly"
          active-class="active"
          :to="{ name: 'Contacts' }"
          id="router-pitch"
        >
          <p>Contacts</p>
        </router-link>

        <router-link
          v-if="!isViewOnly"
          active-class="active"
          :to="{ name: 'EmailTracking' }"
          id="router-pitch"
        >
          <p>Emails</p>
        </router-link>

        <router-link
          v-if="!isViewOnly"
          active-class="active"
          :to="{ name: 'Reports' }"
          id="router-pitch"
        >
          <p>Reports</p>
        </router-link>

        <div style="margin-right: 12px" v-if="isViewOnly" class="auto-left guest-text">
          <p>You're in guest mode. Visit <span @click="goToDemo">ManagrAI</span> to learn more.</p>
        </div>

        <div v-if="!isViewOnly" class="auto-left">
          <div v-if="$route.name === 'Reports'" class="row">
            <p class="searches-used-text">Report credits: {{ reportCredits }}</p>
          </div>

          <div v-if="!isPaid && $route.name !== 'Reports'" class="row wrapper-count">
            <p class="searches-used-text">{{ 20 - searchesUsed }} / 20</p>
            <div style="margin-left: -40px" class="tooltip-count">Remaining monthly credits</div>
          </div>

          <div v-if="$route.name === 'Reports'" class="relative">
            <div @click.stop="toggleShowReports" class="row pointer nav-text">
              Saved Reports
              <img
                v-if="!showSavedReports"
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

            <div v-outside-click="hideReports" v-show="showSavedReports" class="search-dropdown">
              <div class="input">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                  <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M4.1 11.06a6.95 6.95 0 1 1 13.9 0 6.95 6.95 0 0 1-13.9 0zm6.94-8.05a8.05 8.05 0 1 0 5.13 14.26l3.75 3.75a.56.56 0 1 0 .8-.79l-3.74-3.73A8.05 8.05 0 0 0 11.04 3v.01z"
                    fill="currentColor"
                  ></path>
                </svg>
                <input class="search-input" v-model="reportText" :placeholder="`Search...`" />
                <img
                  v-show="reportText"
                  @click="clearText"
                  src="@/assets/images/close.svg"
                  class="invert pointer"
                  height="12px"
                  alt=""
                />
              </div>
              <p class="v-margin" v-if="!reports.length">Nothing here...</p>

              <div class="searches-container">
                <div
                  @mouseenter="setIndex(i)"
                  @mouseLeave="removeIndex"
                  class="row relative"
                  v-for="(report, i) in reports"
                  :key="report.id"
                >
                  <p :title="report.name" @click="selectReport(report.share_url)">
                    {{ report.title }}
                  </p>

                  <img
                    @click="toggleReportDeleteModal(report)"
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

          <div v-if="$route.name === 'PRSummaries'" class="relative">
            <div @click.stop="toggleShowSearches" class="row pointer nav-text">
              Saved Threads
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

            <div v-outside-click="hideSearches" v-show="showSavedSearches" class="search-dropdown">
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
                    v-if="search.meta_data.type === 'news'"
                    src="@/assets/images/globe.svg"
                    height="12px"
                    alt=""
                    @click="selectSearch(search)"
                  />
                  <img
                    class="search-icon"
                    v-else-if="search.meta_data.type === 'social'"
                    src="@/assets/images/thumb.svg"
                    height="12px"
                    alt=""
                    @click="selectSearch(search)"
                  />
                  <img
                    class="search-icon"
                    v-else-if="search.meta_data.type === 'web'"
                    src="@/assets/images/google.svg"
                    height="12px"
                    alt=""
                    @click="selectSearch(search)"
                  />
                  <img
                    class="search-icon"
                    v-else-if="search.meta_data.type === 'discover'"
                    src="@/assets/images/users.svg"
                    height="12px"
                    alt=""
                    @click="selectSearch(search)"
                  />
                  <img
                    class="search-icon"
                    v-else-if="search.meta_data.type === 'write'"
                    src="@/assets/images/brain.svg"
                    height="12px"
                    alt=""
                    @click="selectSearch(search)"
                  />
                  <img
                    class="search-icon"
                    v-else-if="search.meta_data.type === 'trending'"
                    src="@/assets/images/arrow-trend-up.svg"
                    height="12px"
                    alt=""
                    @click="selectSearch(search)"
                  />
                  <p style="margin-left: 0" :title="search.title" @click="selectSearch(search)">
                    {{ search.title }}
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

              <!-- <div class="h-padding">
                <div @click="togglePersonal" class="toggle">
                  <div :class="{ 'active-toggle': personalSearches }" class="toggle-side">
                    <small>Personal</small>
                  </div>

                  <div :class="{ 'active-toggle': !personalSearches }" class="toggle-side">
                    <small>Group</small>
                  </div>
                </div>
              </div> -->
            </div>

            <!-- <div v-outside-click="hideAssists" v-show="showSavedAssist" class="search-dropdown">
              <div class="input">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                  <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M4.1 11.06a6.95 6.95 0 1 1 13.9 0 6.95 6.95 0 0 1-13.9 0zm6.94-8.05a8.05 8.05 0 1 0 5.13 14.26l3.75 3.75a.56.56 0 1 0 .8-.79l-3.74-3.73A8.05 8.05 0 0 0 11.04 3v.01z"
                    fill="currentColor"
                  ></path>
                </svg>
                <input class="search-input" v-model="assistText" :placeholder="`Search...`" />
                <img
                  v-show="assistText"
                  @click="clearText"
                  src="@/assets/images/close.svg"
                  class="invert pointer"
                  height="12px"
                  alt=""
                />
              </div>
              <p class="v-margin" v-if="!assists.length">Nothing here...</p>

              <div class="searches-container">
                <div
                  @mouseenter="setIndex(i)"
                  @mouseLeave="removeIndex"
                  class="row relative"
                  v-for="(assist, i) in assists"
                  :key="assist.id"
                >
                  <p :title="assist.name" @click="selectAssist(assist)">
                    {{ assist.name }}
                  </p>

                  <img
                    @click="toggleAssistDeleteModal(assist)"
                    v-if="hoverIndex === i"
                    class="absolute-icon"
                    src="@/assets/images/trash.svg"
                    height="12px"
                    alt=""
                  />
                </div>
              </div>
            </div> -->
          </div>

          <div class="row right-mar avatar-container">
            <div @click.stop="toggleMenu" class="avatar">{{ getInitials() }}</div>

            <div v-outside-click="hideMenu" v-show="menuOpen" class="avatar-dropdown">
              <p class="dropdown-item" @click="goToSettings">
                <!-- <img class="mar-right" src="@/assets/images/settings.svg" height="14px" alt="" /> -->
                <img class="mar-right" src="@/assets/images/profile.svg" height="13px" alt="" />
                Users
              </p>
              <p class="dropdown-item" @click="goToIntegrations">
                <img class="mar-right" src="@/assets/images/apps.svg" height="13px" alt="" />
                Integrations
              </p>
              <!-- <p class="dropdown-item" @click="goToReports">
                <img class="mar-right" src="@/assets/images/report.svg" height="13px" alt="" />
                Digest
              </p> -->
              <p @click="logOut" class="dropdown-item dropdown-border">
                <img class="mar-right" src="@/assets/images/logout.svg" height="13px" alt="" /> Sign
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
      contactLink: 'https://managr.ai/contact',
      reportsModalOpen: false,
      selectedReport: null,
      deleteReportModalOpen: false,
      personalSearches: true,
      personalDiscoveries: true,
      items: [],
      reportText: '',
      searchText: '',
      pitchText: '',
      assistText: '',
      discoveryText: '',
      showSavedSearches: false,
      showSavedPitches: false,
      showSavedAssist: false,
      showSavedDiscoveries: false,
      showSavedReports: false,
      deleteModelOpen: false,
      deletePitchModelOpen: false,
      deleteAssistModelOpen: false,
      deleteDiscoveryModelOpen: false,
      selectedSearch: null,
      selectedPich: null,
      soonText: 'Transcribe',
      hoverIndex: null,
      showUpdateBanner: false,
      mobileMenuOpen: false,
      hamburgerClicked: false,
      plansModal: false,
      // team: CollectionManager.create({ ModelClass: User }),
      numberOfUsers: 5,
      amountList: [
        5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28,
        29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
        52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74,
        75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97,
        98, 99, 100,
      ],
    }
  },
  async created() {
    if (!this.$route.params.code) {
      this.getThreads()
      this.getSearches()
      this.getPitches()
      this.getAssist()
      this.getDiscoveries()
      this.getReports()
    }
    // await this.team.refresh()
    // this.amountList = this.amountList.filter((item) => item >= this.activeUsers.length)

    // this.numberOfUsers = this.activeUsers.length
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
      this.showSavedAssist = false
      this.showSavedSearches = false
      this.showSavedDiscoveries = false
      this.showSavedReports = false
      this.$emit('close-menu')
      if (this.$route.name === 'Reports' && this.reportCredits < 1) {
        this.reportsModalOpen = true
      } else {
        this.reportsModalOpen = false
      }
    },
  },
  methods: {
    async deleteReport() {
      try {
        await User.api.deleteReport(this.selectedReport.id)
        await this.getReports()

        this.selectReport = null
        this.deleteReportModalOpen = false
        this.$toast('Report removed', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        console.log(e)
      }
    },
    selectReport(url) {
      window.open(url, '_blank')
    },
    hideSearches() {
      this.showSavedSearches = false
    },
    hideReports() {
      this.showSavedReports = false
    },
    hideDiscoveries() {
      this.showSavedDiscoveries = false
    },
    hidePitches() {
      this.showSavedPitches = false
    },
    hideAssists() {
      this.showSavedAssist = false
    },
    hideMenu() {
      this.$emit('close-menu')
    },
    togglePersonal() {
      this.personalSearches = !this.personalSearches
    },
    togglePersonalDiscoveries() {
      this.personalDiscoveries = !this.personalDiscoveries
    },
    setIndex(i) {
      this.hoverIndex = i
    },
    removeIndex() {
      this.hoverIndex = null
    },
    toggleMobileMenu() {
      this.mobileMenuOpen = !this.mobileMenuOpen
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
    toggleReportDeleteModal(report = null) {
      if (report) {
        this.selectedReport = report
      }
      this.deleteReportModalOpen = !this.deleteReportModalOpen
    },
    toggleDeleteModal(search = null) {
      if (search) {
        this.selectedSearch = search
      }
      this.deleteModelOpen = !this.deleteModelOpen
      this.showSavedSearches = false
      this.showSavedPitches = false
      this.showSavedAssist = false
      this.showSavedDiscoveries = false
      this.showSavedReports = false
    },
    togglePitchDeleteModal(pitch = null) {
      if (pitch) {
        this.selectedPitch = pitch
      }
      this.deletePitchModelOpen = !this.deletePitchModelOpen
      this.showSavedSearches = false
      this.showSavedPitches = false
      this.showSavedAssist = false
      this.showSavedDiscoveries = false
      this.showSavedReports = false
    },
    toggleAssistDeleteModal(assist = null) {
      if (assist) {
        this.currentProcess = assist
      }
      this.deleteAssistModelOpen = !this.deleteAssistModelOpen
      this.showSavedSearches = false
      this.showSavedPitches = false
      this.showSavedAssist = false
      this.showSavedDiscoveries = false
      this.showSavedReports = false
    },
    toggleDiscoveryDeleteModal(discovery = null) {
      if (discovery) {
        this.currentDiscovery = discovery
      }
      this.deleteDiscoveryModelOpen = !this.deleteDiscoveryModelOpen
      this.showSavedSearches = false
      this.showSavedPitches = false
      this.showSavedAssist = false
      this.showSavedDiscoveries = false
      this.showSavedReports = false
    },
    async deleteSearch() {
      try {
        await Comms.api
          .deleteThread({
            id: this.selectedSearch.id,
          })
          .then(() => {
            this.$store.dispatch('getThreads')
            this.deleteModelOpen = false
            this.$toast('Thread removed', {
              timeout: 2000,
              position: 'top-left',
              type: 'success',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
          })
      } catch (e) {
        console.log('ERROR DELETING SEARCH', e)
      } finally {
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
            this.$toast('Content removed', {
              timeout: 2000,
              position: 'top-left',
              type: 'success',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
          })
      } catch (e) {
        console.log('ERROR DELETING PITCH', e)
      } finally {
        setTimeout(() => {
          this.showUpdateBanner = false
        }, 2000)
      }
    },
    async deleteProcess() {
      try {
        Comms.api
          .deleteProcess({
            id: this.currentProcess.id,
          })
          .then(() => {
            this.$toast('Process removed', {
              timeout: 2000,
              position: 'top-left',
              type: 'success',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
            this.getAssist()
            this.toggleAssistDeleteModal()
          })
      } catch (e) {
        console.log(e)
        this.$toast(`${e}`, {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async deleteDiscovery() {
      try {
        Comms.api
          .deleteDiscovery({
            id: this.currentDiscovery.id,
          })
          .then(() => {
            this.$toast('Discovery removed', {
              timeout: 2000,
              position: 'top-left',
              type: 'success',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
            this.getDiscoveries()
            this.toggleDiscoveryDeleteModal()
          })
      } catch (e) {
        console.log(e)
        this.$toast(`${e}`, {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
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
        const sessionId = response.session_id

        const stripe = await this.$stripe()

        const result = await stripe.redirectToCheckout({
          sessionId: sessionId,
        })

        if (result.error) {
          console.log('error', result.error)
        }
        this.numberOfUsers = 5
      } catch (e) {
        console.log('Error in purchasePro: ', e)
      }
    },
    purchaseCredits() {
      window.open(this.contactLink, '_blank')
    },
    toggleAllSearches() {
      this.$emit('close-menu')
      this.showSavedSearches = false
      this.showSavedPitches = false
      this.showSavedDiscoveries = false
      this.showSavedReports = false
    },
    selectSearch(search) {
      this.toggleAllSearches()
      this.$store.dispatch('setSearch', search)
    },
    selectPitch(pitch) {
      this.toggleShowPitches()
      this.$store.dispatch('setPitch', pitch)
    },
    selectAssist(assist) {
      this.toggleShowAssist()
      this.$store.dispatch('setAssist', assist)
    },
    selectDiscovery(discovery) {
      this.toggleShowDiscoveries()
      this.$store.dispatch('setDiscovery', discovery)
    },
    toggleShowSearches() {
      this.$emit('close-menu')
      this.showSavedSearches = !this.showSavedSearches
    },
    toggleShowPitches() {
      this.$emit('close-menu')
      this.showSavedPitches = !this.showSavedPitches
    },
    toggleShowAssist() {
      this.$emit('close-menu')
      this.showSavedAssist = !this.showSavedAssist
    },
    toggleShowDiscoveries() {
      this.$emit('close-menu')
      this.showSavedDiscoveries = !this.showSavedDiscoveries
    },
    toggleShowReports() {
      this.$emit('close-menu')
      this.showSavedReports = !this.showSavedReports
    },
    getSearches() {
      this.$store.dispatch('getSearches')
    },
    getThreads() {
      this.$store.dispatch('getThreads')
    },
    getPitches() {
      this.$store.dispatch('getPitches')
    },
    getAssist() {
      this.$store.dispatch('getAssist')
    },
    getDiscoveries() {
      this.$store.dispatch('getDiscoveries')
    },
    getReports() {
      this.$store.dispatch('getReports')
    },
    goHome() {
      if (this.isViewOnly) {
        // window.open('https://managr.ai', '_blank')
      } else {
        this.$router.go()
      }
    },
    goToDemo() {
      window.open('https://managr.ai', '_blank')
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
      this.showSavedAssist = false
      this.showSavedDiscoveries = false
      this.$emit('toggle-menu')
    },
    clearText() {
      this.searchText = ''
      this.pitchText = ''
      this.assistText = ''
      this.discoveryText = ''
      this.reportText = ''
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
    isViewOnly() {
      return this.$store.state.viewOnly
    },
    unfilteredSearches() {
      if (this.personalSearches) {
        return this.$store.state.allThreads.filter((thread) => thread.user === this.user.id)
      } else {
        return this.$store.state.allThreads
      }
    },
    listName() {
      return this.$store.state.listName
    },
    // activeUsers() {
    //   return this.team.list.filter((user) => user.isActive)
    // },
    unfilteredPitches() {
      return this.$store.state.allPitches
    },
    unfilteredAssist() {
      return this.$store.state.allAssist
    },
    unfilteredDiscoveries() {
      if (this.personalDiscoveries) {
        return this.$store.state.allDiscoveries.filter(
          (discovery) => discovery.user === this.user.id,
        )
      } else {
        return this.$store.state.allDiscoveries
      }
    },
    unfilteredReports() {
      return this.$store.state.allReports
    },
    searches() {
      if (this.unfilteredSearches.length) {
        return this.unfilteredSearches.filter((search) =>
          search.title.toLowerCase().includes(this.searchText.toLowerCase()),
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
    reports() {
      if (this.unfilteredReports.length) {
        return this.unfilteredReports.filter((report) =>
          report.title.toLowerCase().includes(this.reportText.toLowerCase()),
        )
      } else return []
    },
    assists() {
      if (this.unfilteredAssist.length) {
        return this.unfilteredAssist.filter((assist) =>
          assist.name.toLowerCase().includes(this.assistText.toLowerCase()),
        )
      } else return []
    },
    discoveries() {
      if (this.unfilteredDiscoveries.length) {
        return this.unfilteredDiscoveries.filter((discovery) =>
          discovery.name.toLowerCase().includes(this.discoveryText.toLowerCase()),
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
      return !!this.$store.state.user.organizationRef.isPaid
    },
    reportCredits() {
      return !!this.$store.state.user.organizationRef.metaData
        ? this.$store.state.user.organizationRef.metaData.reportCredits
        : 0
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
    user() {
      return this.$store.state.user
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
  #hamburger {
    display: block !important;
  }

  #relative-mobile {
    display: block !important;
    position: fixed;
    // top: 24px;
    // right: 80px;
    top: 0;
    right: 0;
    padding: 16px 32px 16px 0;
    z-index: 20100;
    background: white;
  }

  #nav {
    display: none;
  }
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

.active-toggle {
  background-color: white;
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 3px 11px rgba(0, 0, 0, 0.1);
  padding: 6px 12px;
}

.toggle {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  background-color: $off-white;
  cursor: pointer;
  width: fit-content;
  padding: 2px 1px;
  border-radius: 16px;

  small {
    font-size: 13px;
    margin: 0 4px;
  }
}

.toggle-side {
  width: 80px;
  padding: 6px 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(0, 0, 0, 0.5);
}

.h-padding {
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

#hamburger {
  display: none;
  cursor: pointer;
  position: fixed;
  // top: 24px;
  // left: 32px;
  top: 0;
  left: 0;
  padding: 16px 0 16px 16px;
  z-index: 20100;
  background-color: white;
  width: 100%;

  img {
    filter: invert(40%);
  }
}

.close-menu {
  font-family: $thin-font-family;
  font-size: 14px;
}

#relative-mobile {
  display: none;
}

.aligned-right {
  position: absolute;
  right: 16px;
  top: 16px;
  z-index: 200000;
  background-color: white;
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

.beta-tag-small {
  letter-spacing: 1px;
  margin-left: 8px;
  opacity: 1 !important;

  p {
    background-color: $graper;
    color: white;
    border-radius: 6px;
    padding: 4px 6px;
    font-size: 11px;
    font-family: $base-font-family;
    cursor: text;

    // &:hover {
    //   opacity: 0.8;
    //   cursor: pointer;
    // }
  }
}

.guest-text {
  span {
    color: $lite-blue;
    cursor: pointer;
  }
}

.beta-tag {
  letter-spacing: 1px;
  margin-left: 8px;

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
  margin-bottom: 0.25rem;
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

  @media only screen and (max-width: 600px) {
    top: 56px;
    right: 8px;
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
  }
}

.mobile-nav {
  z-index: 200000;
  min-height: 22vh;
  height: fit-content;
  width: 60vw;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 5px;
  background-color: white;
  display: flex;
  flex-direction: column;
  position: absolute;
  top: 36px;
  left: 10px;

  a {
    text-decoration: none;
    font-weight: 400;
    font-family: $thin-font-family;
    color: $light-gray-blue;
    font-size: 13px;
    padding: 4px 16px;
    margin: 0;

    img {
      transition: all 0.2s;
    }
  }

  a:hover {
    opacity: 0.6;
  }
}
.logo {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  // img {

  //   filter: brightness(0) invert(23%) sepia(19%) saturate(984%) hue-rotate(162deg) brightness(92%)
  //     contrast(87%);
  // }
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

  img {
    margin-left: 8px;
  }
}
.light-gray-blue {
  color: $light-gray-blue;
}

#nav a {
  text-decoration: none;
  font-weight: 400;
  font-family: $thin-font-family;
  // color: #6b6b6b;
  color: $dark-black-blue;
  font-size: 14px;
  padding: 6px 4px;
  margin: 0 12px;

  img {
    transition: all 0.2s;
  }
}
a:hover {
  opacity: 0.7;
}
.active {
  // color: $turq !important;
  position: relative;
  font-family: $base-font-family !important;
  border-bottom: 1px solid $dark-black-blue;
  // background-color: $white-blue;
}

.active-mobile {
  color: $dark-black-blue;
  position: relative;
  background-color: $off-white;
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
  font-size: 14px;
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

.small-bold-text {
  font-size: 16px;
  span {
    font-family: $base-font-family;
  }
}

.bold-txt {
  font-family: $base-font-family;
}

.large-txt {
  font-size: 24px;
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
  padding-bottom: 0rem;
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

.paid-modal {
  margin-top: 132px;
  font-family: $thin-font-family;
}
.regen-container {
  width: 500px;
  max-height: 500px;
  position: relative;
  overflow-y: scroll;
  font-family: $thin-font-family;
  // :style="isMobile ? '' : 'width: 610px; min-height: 100px; '"

  @media only screen and (max-width: 600px) {
    font-size: 13px !important;
    width: 100% !important;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.paid-header {
  position: sticky;
  top: 0;
  background-color: white;
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}
.sticky-header {
  position: sticky;
  top: 0;
}

.paid-item:hover {
  cursor: pointer;
  opacity: 0.4;
}

.paid-center {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.aligned-left {
  align-items: flex-start;
}
.regen-header-title {
  font-size: 20px;
  font-family: $base-font-family;
  font-weight: 200;
  margin: 0.25rem 0;
}
.regen-header-subtitle {
  font-size: 14px;

  margin: 0.5rem 0;
}
.regen-body {
  margin: 0.5rem 0;
  border-bottom: 1px solid $soft-gray;
}
.paid-body {
  margin: 0.5rem 0;

  // input {
  //   font-family: ;
  // }
}
.regen-body-title {
  text-align: center;
  width: 90%;
  font-size: 16px !important;
  line-height: 1.5;
  margin: 0 0 0 0;
}
.paid-title {
  margin-top: 0;
  margin-bottom: 2rem;
  font-family: $base-font-family;
  font-weight: 200;
  font-size: 24px;
}
.paid-footer {
  position: sticky;
  background: white;
  width: 100%;
  bottom: 0;
  padding-top: 16px;
  // padding-bottom: 8px;
  margin: 1rem 0 0 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.save-button {
  @include dark-blue-button();
  &:hover {
    scale: 1;
    opacity: 0.9;
    box-shadow: none;
  }
  margin-left: 0.5rem;
}
</style>
