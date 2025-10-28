# Kubewarden Cosign Demo: Enforcing Signed Images

This demo showcases how **Kubewarden** can enforce that only container images signed with **Cosign** are allowed to run in a Kubernetes cluster, enhancing supply chain security.

We assume two versions of an application image already exist in the registry:
* `:v1.0`: Represents the legitimate version, which **has been signed** using Cosign after being pushed.
* `:v1.1`: Represents an updated (potentially malicious or accidental) version, which **has NOT been signed**.

A Kubewarden policy will **block** the deployment of the unsigned `:v1.1` image while **allowing** the signed `:v1.0` image.

---

## Prerequisites

* `cosign`
* `kubectl`
* `oras` CLI
* Access to a Kubernetes cluster with Kubewarden installed (PolicyServer named `default`).
* The container images `${IMAGE_URI}:v1.0` and `${IMAGE_URI}:v1.1` already built and pushed to the registry (e.g., `ghcr.io/lucabarze-suse/kubewarden-cosign-demo`).
* The demo repository cloned locally, containing `policy.yaml`, `pod-signed.yaml`, and `pod-unsigned.yaml`.

---

## Preparation (Verification of the Setup)

We assume the images are already pushed. The **crucial preparation step** already performed was signing **only** the `v1.0` image after it was pushed.

1.  **Set Environment Variables:**
    ```bash
    # Adjust to your registry and repository
    export IMAGE_URI="ghcr.io/lucabarze-suse/kubewarden-cosign-demo"
    # Adjust to your registry username if needed for verification tools
    export REGISTRY_USER="lucabarze-suse" 
    
2.  **(DONE OFFLINE) Signing v1.0:**
    # We need the exact digests for verification (replace with actual digests)
    export DIGEST_V1_0="sha256:<digest-v1.0>" 
    export DIGEST_V1_1="sha256:<digest-v1.1>" 
    ```
    *Note: You can retrieve digests using `podman inspect ${IMAGE_URI}:<tag> --format '{{.Digest}}'` or `oras manifest fetch ${IMAGE_URI}:<tag> --descriptor | jq -r .digest` if you don't have them.*

    The following command was previously executed to sign the `v1.0` image:
    ```bash
    # Command executed before the demo (DO NOT RUN LIVE):
    # export COSIGN_PASSWORD=$CR_PAT 
    # cosign sign --yes -u "$REGISTRY_USER" \
    #   -a "creator=Your Name" -a "context=Demo Kubewarden" \
    #   "${IMAGE_URI}@${DIGEST_V1_0}" 
    ```

---

## Live Demo Steps

1.  **Show Registry Contents (Signed vs. Unsigned):**
    * Show that `v1.1` only has the image layer:
        ```bash
        oras discover --format tree "${IMAGE_URI}@${DIGEST_V1_1}"
        ```
    * Show that `v1.0` has the image layer **plus** the signature artifact:
        ```bash
        oras discover --format tree "${IMAGE_URI}@${DIGEST_V1_0}"
        ```

2.  **Verify Signatures with Cosign:**
    * Show `cosign verify` failing for `v1.1`:
        ```bash
        # Adjust identity/issuer if signing was done differently
        cosign verify \
          --certificate-identity "luca.barze@suse.com" \
          --certificate-oidc-issuer "https://github.com/login/oauth" \
          "${IMAGE_URI}@${DIGEST_V1_1}"
        # EXPECT ERROR
        ```
    * Show `cosign verify` succeeding for `v1.0`:
        ```bash
        cosign verify \
          --certificate-identity "luca.barze@suse.com" \
          --certificate-oidc-issuer "[https://github.com/login/oauth](https://github.com/login/oauth)" \
          "${IMAGE_URI}@${DIGEST_V1_0}"
        # EXPECT SUCCESS + Signature details
        ```

3.  **Apply the Kubewarden Policy:**
    * Apply the `AdmissionPolicy` from the file:
        ```bash
        # Ensure image URI in policy.yaml matches $IMAGE_URI
        kubectl apply -f policy.yaml
        ```
    * *(Optional) Wait for the policy to become active:*
        ```bash
        kubectl get admissionpolicy -n default enforce-signed-demo-images -w --output-condition=jsonpath='{.status.policyStatus}'=active
        ```

4.  **Attempt to Deploy the Unsigned Pod (v1.1):**
    * Try applying the Pod manifest from the file:
        ```bash
        # Ensure image URI in pod-unsigned.yaml matches $IMAGE_URI
        kubectl apply -f pod-unsigned.yaml
        ```
5.  **Deploy the Signed Pod (v1.0):**
    * Apply the Pod manifest from the file:
        ```bash
        # Ensure image URI in pod-signed.yaml matches $IMAGE_URI
        kubectl apply -f pod-signed.yaml
        ```
6.  **(Optional but Recommended) Show Image Digest Mutation:**
    * Inspect the running Pod:
        ```bash
        kubectl get pod demo-pod-signed -n default -o yaml
        ```
    * **The `image:` field now uses the immutable digest `${IMAGE_URI}@${DIGEST_V1_0}` instead of the tag `:v1.0`.** 

---

## Conclusion

This demo illustrates how Kubewarden, combined with Cosign, provides a robust mechanism to enforce image signature verification directly within the Kubernetes admission flow, significantly improving the security posture of your cluster.
