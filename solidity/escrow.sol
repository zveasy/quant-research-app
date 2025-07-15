// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/// @title Hash-Time-Locked DVP Escrow
/// @notice Depositor exchanges tokenA for tokenB with a counterparty.
/// @dev Funds can be refunded if the timelock expires before swap.
contract Escrow {
    address public immutable depositor;
    address public immutable counterparty;
    IERC20 public immutable tokenA;
    IERC20 public immutable tokenB;
    bytes32 public immutable hashlock;
    uint256 public immutable timelock;

    bool public depositedA;
    bool public depositedB;
    bool public swapped;

    /// @param _depositor owner of tokenA
    /// @param _counterparty owner of tokenB
    /// @param _tokenA address of tokenA contract
    /// @param _tokenB address of tokenB contract
    /// @param _hashlock keccak256 hash of secret
    /// @param _timelock UNIX time for refund availability
    constructor(
        address _depositor,
        address _counterparty,
        address _tokenA,
        address _tokenB,
        bytes32 _hashlock,
        uint256 _timelock
    ) {
        depositor = _depositor;
        counterparty = _counterparty;
        tokenA = IERC20(_tokenA);
        tokenB = IERC20(_tokenB);
        hashlock = _hashlock;
        timelock = _timelock;
    }

    /// Emitted when a party deposits tokens
    event Deposited(address indexed from, uint256 amount);
    /// Emitted on successful swap
    event Swapped();
    /// Emitted when both parties are refunded
    event Refunded();

    /// @notice Depositor sends tokenA
    function depositA(uint256 amount) external {
        require(msg.sender == depositor, "not depositor");
        require(!depositedA, "already");
        require(tokenA.transferFrom(msg.sender, address(this), amount), "transfer failed");
        depositedA = true;
        emit Deposited(msg.sender, amount);
    }

    /// @notice Counterparty sends tokenB
    function depositB(uint256 amount) external {
        require(msg.sender == counterparty, "not counterparty");
        require(!depositedB, "already");
        require(tokenB.transferFrom(msg.sender, address(this), amount), "transfer failed");
        depositedB = true;
        emit Deposited(msg.sender, amount);
    }

    /// @notice Executes swap when secret provided
    function swap(bytes32 preimage) external {
        require(depositedA && depositedB, "missing deposit");
        require(!swapped, "done");
        require(keccak256(abi.encodePacked(preimage)) == hashlock, "bad secret");
        swapped = true;
        tokenA.transfer(counterparty, tokenA.balanceOf(address(this)));
        tokenB.transfer(depositor, tokenB.balanceOf(address(this)));
        emit Swapped();
    }

    /// @notice Refunds both sides after timeout
    function refund() external {
        require(block.timestamp >= timelock, "not expired");
        require(!swapped, "done");
        if (depositedA) {
            tokenA.transfer(depositor, tokenA.balanceOf(address(this)));
        }
        if (depositedB) {
            tokenB.transfer(counterparty, tokenB.balanceOf(address(this)));
        }
        emit Refunded();
    }
}
